-- 0009 · Clonar un insumo (clonar y mantener · clonar y sustituir) y la homologación de la clave vieja
--
-- `1-mundo/CONOCIMIENTO.md` §8.4 y §16.2, `MODELO.md` §4 y §4b, D-478. La clave nunca se reescribe: para corregir un prefijo que
-- engaña (P-11: las 79 trabes y mallas con `AUX-`) nace un **clon** con la clave correcta y el contenido del original.
--
-- - **Clonar y mantener:** el original sigue vivo; los dos se usan (la trabe T-3 y la T-4).
-- - **Clonar y sustituir:** todo lo que apuntaba al original pasa al clon, y **la clave vieja sigue entrando**: un archivo de OPUS
--   que la traiga se lee como el clon (homologación, §16.2). El viaje de vuelta —la clave vieja sigue saliendo hacia otros
--   sistemas hasta que alguien lo autorice— se guarda como bandera; no hay todavía quien exporte (B-08).
--
-- Una versión y sus líneas no se reescriben: sustituir crea **versión nueva** de cada concepto que citaba al original, con la
-- misma receta salvo la clave y el mismo PU, y los renglones de presupuesto en diseño pasan a fijarla.

-- `armar_arbol` (D-472) clasificaba como `auxiliar` a todo compuesto de material; `CONOCIMIENTO.md` §10.4 dice lo contrario
-- («la trabe NO es un auxiliar»): un compuesto de material es un material. Se corrige lo ya guardado.
UPDATE nodo SET categoria = 'material' WHERE categoria = 'auxiliar';

ALTER TABLE carga DROP CONSTRAINT carga_tipo_check;
ALTER TABLE carga ADD CONSTRAINT carga_tipo_check CHECK (tipo IN ('archivos', 'contratacion', 'clonacion'));

CREATE TABLE clon (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    original_id   bigint NOT NULL REFERENCES nodo,
    clon_id       bigint NOT NULL UNIQUE REFERENCES nodo,        -- un clon nace de un solo original
    modo          text   NOT NULL CHECK (modo IN ('mantener', 'sustituir')),
    -- si modo = sustituir, la clave vieja sigue entrando y se resuelve al clon; en mantener no hay clave vieja que resolver
    reconoce_clave_vieja_al_importar boolean NOT NULL,
    -- la clave vieja sigue saliendo hacia otros sistemas hasta que el usuario autorice dejar de hacerlo
    exporta_clave_vieja boolean NOT NULL DEFAULT true,
    usuario       text   NOT NULL CHECK (usuario <> ''),
    rol           text   NOT NULL CHECK (rol <> ''),
    carga_id      bigint NOT NULL REFERENCES carga,               -- la clonación: de ahí salen el clon y las versiones nuevas
    resumen       jsonb  NOT NULL,                                -- qué se redirigió: concepto por concepto
    creada_en     timestamptz NOT NULL DEFAULT now(),
    CHECK (original_id <> clon_id),
    CHECK (modo = 'sustituir' OR NOT reconoce_clave_vieja_al_importar)
);
CREATE INDEX clon_del_original ON clon (original_id);

-- Un clon no se reescribe ni se borra; lo único que cambia es que alguien autorice dejar de exportar la clave vieja (y no vuelve).
CREATE FUNCTION clon_solo_se_cierra() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'UPDATE'
       AND OLD.exporta_clave_vieja AND NOT NEW.exporta_clave_vieja
       AND NEW.id = OLD.id AND NEW.original_id = OLD.original_id AND NEW.clon_id = OLD.clon_id AND NEW.modo = OLD.modo
       AND NEW.reconoce_clave_vieja_al_importar = OLD.reconoce_clave_vieja_al_importar AND NEW.usuario = OLD.usuario
       AND NEW.rol = OLD.rol AND NEW.carga_id = OLD.carga_id AND NEW.resumen = OLD.resumen AND NEW.creada_en = OLD.creada_en THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'un clon no se reescribe ni se borra: solo se autoriza dejar de exportar su clave vieja, y no se vuelve a abrir';
END $$;

CREATE TRIGGER clon_solo_se_cierra BEFORE UPDATE OR DELETE ON clon
    FOR EACH ROW EXECUTE FUNCTION clon_solo_se_cierra();

-- Quién clona: una función nueva de `MODELO.md` §5b, propuesta, para Control de obra (gobierno cruzado entre obras). Se corrige
-- en la tabla, sin tocar esquema.
INSERT INTO funcion_atomica (clave) VALUES ('clonar_insumo');

INSERT INTO rol_funcion (rol_id, funcion_id)
SELECT r.id, f.id FROM (VALUES ('control_de_obra', 'clonar_insumo')) AS a (rol, funcion)
JOIN rol r ON r.clave = a.rol
JOIN funcion_atomica f ON f.clave = a.funcion;
