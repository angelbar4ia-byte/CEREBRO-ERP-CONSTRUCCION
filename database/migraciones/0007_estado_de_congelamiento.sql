-- 0007 · El estado de congelamiento: contratar un subárbol del presupuesto
--
-- `1-mundo/CONOCIMIENTO.md` §1.4 y `MODELO.md` §3 (hallazgo 6): el estado es **del nodo, no del presupuesto**. Los planos llegan por
-- partes y se contrata por partes: cimentación entra a contrato mientras acabados sigue en diseño. Un nodo estructural pasa a
-- `contratado` y **su subárbol se contrata completo**; los descendientes lo heredan.
--
-- Contratar tiene dos efectos, ambos en una sola transacción (`MODELO.md` §4a, «dos disparadores de versión»):
--   1. cada concepto del subárbol queda con su PU **fijado a ese momento**: si el PU de hoy no es el de la versión vigente, nace una
--      versión nueva con la misma receta y el PU de hoy; y cada renglón del subárbol fija la versión vigente;
--   2. el subárbol queda congelado: ni su cantidad ni la versión que fija se tocan (lo garantiza el disparador de abajo). Lo que
--      cambie después va por control de cambio, que agrega, no edita (`CONOCIMIENTO.md` §13.4).
-- La base no sabe nada de precios: lo que calcula el PU de hoy es el motor de cálculo y llega ya hecho en el plan.

-- una contratación es un acto con su autor, y deja su fila en `carga` (las versiones nuevas citan una carga): el tipo distingue
-- la que trajo archivos de la que contrató
ALTER TABLE carga ADD COLUMN tipo text NOT NULL DEFAULT 'archivos' CHECK (tipo IN ('archivos', 'contratacion'));

CREATE TABLE estado_congelamiento (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nodo_id     bigint NOT NULL REFERENCES nodo,                  -- solo estructurales: el subárbol que se contrata
    estado      text   NOT NULL CHECK (estado IN ('diseño', 'contratado')),
    fecha       timestamptz NOT NULL DEFAULT now(),
    usuario     text   NOT NULL CHECK (usuario <> ''),
    rol         text   NOT NULL CHECK (rol <> ''),
    carga_id    bigint NOT NULL REFERENCES carga,                 -- la contratación que lo fijó: de ahí salen las versiones nuevas
    resumen     jsonb  NOT NULL                                   -- qué se fijó: conceptos, versiones nuevas, totales antes y después
);
-- un nodo se contrata una vez; deshacerlo no está definido en el cerebro (sería un control de cambio) y no se ofrece
CREATE UNIQUE INDEX estado_congelamiento_contratado_unico ON estado_congelamiento (nodo_id) WHERE estado = 'contratado';
CREATE INDEX estado_congelamiento_del_nodo ON estado_congelamiento (nodo_id, id);

CREATE FUNCTION estado_congelamiento_solo_de_estructurales() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF (SELECT rol FROM nodo WHERE id = NEW.nodo_id) <> 'estructural' THEN
        RAISE EXCEPTION 'el estado de congelamiento es de un nodo estructural: el nodo % no lo es', NEW.nodo_id;
    END IF;
    RETURN NEW;
END $$;

CREATE FUNCTION estado_congelamiento_solo_se_agrega() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'el estado de congelamiento no se reescribe ni se borra: un estado nuevo es una fila nueva';
END $$;

CREATE TRIGGER estado_congelamiento_estructural BEFORE INSERT ON estado_congelamiento
    FOR EACH ROW EXECUTE FUNCTION estado_congelamiento_solo_de_estructurales();
CREATE TRIGGER estado_congelamiento_solo_se_agrega BEFORE UPDATE OR DELETE ON estado_congelamiento
    FOR EACH ROW EXECUTE FUNCTION estado_congelamiento_solo_se_agrega();

-- Lo contratado está congelado: un renglón de presupuesto (una línea sin versión) cuyo bloque, o algún bloque de arriba, está
-- contratado no se edita ni se borra. Agregar sí se puede: «solo admite adiciones al final» (`CONOCIMIENTO.md` §1.4).
CREATE FUNCTION presupuesto_contratado_no_se_toca() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (
        WITH RECURSIVE arriba (id) AS (
            SELECT OLD.padre_id
            UNION
            SELECT c.padre_id FROM composicion c JOIN arriba a ON c.hijo_id = a.id WHERE c.version_id IS NULL
        )
        SELECT 1 FROM estado_congelamiento e JOIN arriba a ON a.id = e.nodo_id WHERE e.estado = 'contratado'
    ) THEN
        RAISE EXCEPTION 'el renglón % está en un subárbol contratado: no se edita ni se borra, se agrega por control de cambio', OLD.id;
    END IF;
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER presupuesto_contratado_no_se_toca BEFORE UPDATE OR DELETE ON composicion
    FOR EACH ROW WHEN (OLD.version_id IS NULL) EXECUTE FUNCTION presupuesto_contratado_no_se_toca();

-- Quién contrata: una función nueva de `MODELO.md` §5b, propuesta, para Control de obra (gobierno cruzado entre obras, el mismo
-- criterio de las demás). Se corrige en la tabla, sin tocar esquema.
INSERT INTO funcion_atomica (clave) VALUES ('contratar_subarbol');

INSERT INTO rol_funcion (rol_id, funcion_id)
SELECT r.id, f.id FROM (VALUES ('control_de_obra', 'contratar_subarbol')) AS a (rol, funcion)
JOIN rol r ON r.clave = a.rol
JOIN funcion_atomica f ON f.clave = a.funcion;
