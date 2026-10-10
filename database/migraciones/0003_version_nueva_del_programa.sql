-- 0003 · La versión nueva de un programa
--
-- El planeador revisa su programa y lo vuelve a subir (`1-mundo/PROGRAMA-CPM.md` §4.8). El programa base no cambia
-- nunca, así que la versión nueva es **otro programa** que dice de cuál viene, y las ediciones que seguían teniendo
-- sentido pasan a él con su autor, su rol y su fecha. Cada una dice de qué edición de la versión anterior viene, y el
-- programa guarda el traspaso: cuántas pasaron y cuáles no, con su motivo, para que se pueda ver después.
--
-- La cadena es una sola: un programa tiene a lo más una versión nueva directa.

ALTER TABLE programa
    ADD COLUMN version_de  bigint REFERENCES programa,
    ADD COLUMN traspaso    jsonb,
    ADD CONSTRAINT programa_traspaso_con_version CHECK ((version_de IS NULL) = (traspaso IS NULL)),
    ADD CONSTRAINT programa_no_es_version_de_si_mismo CHECK (version_de IS NULL OR version_de <> id);

CREATE UNIQUE INDEX programa_una_version_nueva ON programa (version_de) WHERE version_de IS NOT NULL;

ALTER TABLE edicion_programa
    ADD COLUMN heredada_de bigint REFERENCES edicion_programa;

-- la bitácora sigue sin reescribirse: lo nuevo, `heredada_de`, tampoco cambia al revertir
CREATE OR REPLACE FUNCTION edicion_programa_solo_se_agrega() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'la bitácora de ediciones no se borra';
    END IF;
    IF OLD.estado = 'aplicada' AND NEW.estado = 'revertida'
       AND NEW.id = OLD.id AND NEW.programa_id = OLD.programa_id AND NEW.secuencia = OLD.secuencia
       AND NEW.edicion = OLD.edicion AND NEW.datos = OLD.datos AND NEW.rol = OLD.rol
       AND NEW.usuario = OLD.usuario AND NEW.impacto = OLD.impacto AND NEW.creada_en = OLD.creada_en
       AND NEW.origen IS NOT DISTINCT FROM OLD.origen
       AND NEW.heredada_de IS NOT DISTINCT FROM OLD.heredada_de THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'una edición aplicada solo puede pasar a revertida';
END;
$$;
