-- 0006 · El programa cuelga del presupuesto
--
-- `1-mundo/MODELO.md` §5c: `ACTIVIDAD` tiene `concepto_id` y `presupuesto_id`. Hasta ahora `programa_fila` citaba un `oid` suelto y
-- `programa.presupuesto_id` era una columna sin tabla a la que apuntar (migración 0001). Con `PRESUPUESTO` y `NODO` (0005), el programa
-- se cuelga: **el programa dice de qué presupuesto es, y cada fila dice a qué se refiere en él.**
--
-- - Una fila de bloque (capítulo, subcapítulo, nivel 2 o 3) se refiere a un **nodo estructural** del presupuesto: `nodo_id`.
-- - Una partida se refiere a un **renglón**, que es una línea de `COMPOSICION` del bloque al concepto: `renglon_id`. No al concepto
--   a secas: el mismo concepto está en muchos lugares de un presupuesto y cada lugar tiene su cantidad y su lugar en el programa.
--   El concepto de la partida es `composicion.hijo_id`.
-- - Una fila sin con qué casarse queda sin enlace y se dice; nada se inventa.
--
-- La bitácora de ediciones sigue citando `oid` —la identidad de la partida *en el programa*—: el enlace es un atributo de la fila, no
-- su identidad, así que lo ya editado no se toca. Lo que se enlaza no se cambia: un enlace nuevo se agrega, uno puesto no se mueve.
-- Colgar es una decisión de quien puede editar la estructura del programa y queda dicha: quién, con qué rol, cuándo y qué cuadró
-- y qué no (`programa_colgadura`, que solo se agrega). Colgar no es editar: no sube `programa.version` ni toca la bitácora.

ALTER TABLE programa
    ADD CONSTRAINT programa_presupuesto FOREIGN KEY (presupuesto_id) REFERENCES presupuesto;

ALTER TABLE programa_fila
    ADD COLUMN nodo_id    bigint REFERENCES nodo,
    ADD COLUMN renglon_id bigint REFERENCES composicion,
    ADD CONSTRAINT programa_fila_un_solo_enlace CHECK (nodo_id IS NULL OR renglon_id IS NULL);

-- un nodo o un renglón del presupuesto lo ocupa a lo más una fila de cada programa
CREATE UNIQUE INDEX programa_fila_nodo_unico    ON programa_fila (programa_id, nodo_id)    WHERE nodo_id IS NOT NULL;
CREATE UNIQUE INDEX programa_fila_renglon_unico ON programa_fila (programa_id, renglon_id) WHERE renglon_id IS NOT NULL;

CREATE FUNCTION programa_el_enlace_no_se_mueve() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_TABLE_NAME = 'programa' THEN
        IF OLD.presupuesto_id IS NOT NULL AND NEW.presupuesto_id IS DISTINCT FROM OLD.presupuesto_id THEN
            RAISE EXCEPTION 'el programa % ya cuelga del presupuesto %: no se cambia, se sube otro programa', OLD.id, OLD.presupuesto_id;
        END IF;
    ELSE
        IF (OLD.nodo_id IS NOT NULL AND NEW.nodo_id IS DISTINCT FROM OLD.nodo_id)
           OR (OLD.renglon_id IS NOT NULL AND NEW.renglon_id IS DISTINCT FROM OLD.renglon_id) THEN
            RAISE EXCEPTION 'la fila % del programa % ya está enlazada: un enlace puesto no se mueve', OLD.oid, OLD.programa_id;
        END IF;
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER programa_presupuesto_no_se_mueve BEFORE UPDATE ON programa
    FOR EACH ROW EXECUTE FUNCTION programa_el_enlace_no_se_mueve();
CREATE TRIGGER programa_fila_enlace_no_se_mueve BEFORE UPDATE ON programa_fila
    FOR EACH ROW EXECUTE FUNCTION programa_el_enlace_no_se_mueve();

-- Cada vez que se cuelga, o que una versión nueva hereda los enlaces de la anterior, queda una fila: de dónde salieron los enlaces.
CREATE TABLE programa_colgadura (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    programa_id    bigint NOT NULL REFERENCES programa,
    presupuesto_id bigint NOT NULL REFERENCES presupuesto,
    usuario        text   NOT NULL CHECK (usuario <> ''),
    rol            text   NOT NULL CHECK (rol <> ''),
    nuevos         integer NOT NULL CHECK (nuevos >= 0),          -- los enlaces que esta vez se pusieron
    resumen        jsonb  NOT NULL,                               -- qué cuadró y qué no: ver `core/colgado.py`
    creada_en      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX programa_colgadura_del_programa ON programa_colgadura (programa_id, id);

CREATE FUNCTION colgadura_solo_se_agrega() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'la bitácora de colgaduras no se reescribe ni se borra: una colgadura nueva es una fila nueva';
END $$;

CREATE TRIGGER programa_colgadura_solo_se_agrega BEFORE UPDATE OR DELETE ON programa_colgadura
    FOR EACH ROW EXECUTE FUNCTION colgadura_solo_se_agrega();
