-- 0008 · Reconciliar un presupuesto que ya existe
--
-- `1-mundo/CONOCIMIENTO.md` §1.4, §2.3 y §2.9 y `MODELO.md` §3: un presupuesto que ya está guardado y llega otra vez con otras
-- cantidades, con renglones nuevos o sin renglones que tenía, se **reconcilia**, no se pisa. En diseño «renumera libre»; lo contratado
-- no se toca (0007). Lo que cambia queda con su historia: ninguna cantidad se pierde.
--
-- - Una **alta** es un renglón o un bloque nuevo; entra con la versión vigente de su concepto.
-- - Una **baja** no borra: el renglón o el bloque queda marcado con la carga que lo dio de baja. No se puede borrar porque el
--   programa lo cita (`programa_fila.renglon_id`, `nodo_id`, migración 0006) y porque la historia es de quien la lea después.
--   Lo que está dado de baja no cuenta: no sale en el presupuesto, ni en el motor de cálculo, ni ocupa su lugar.
-- - Un **cambio de cantidad** o de lugar actualiza el renglón —su identidad, a la que se cuelga el programa, no cambia— y deja una fila
--   en `renglon_historia`, que solo se agrega.

ALTER TABLE composicion
    ADD COLUMN baja_carga_id bigint REFERENCES carga,
    ADD CONSTRAINT composicion_baja_solo_de_presupuesto CHECK (baja_carga_id IS NULL OR version_id IS NULL);

ALTER TABLE nodo ADD COLUMN baja_carga_id bigint REFERENCES carga;

-- el lugar de un renglón vivo es único dentro de su bloque; el de uno dado de baja ya no cuenta
DROP INDEX composicion_orden_en_el_presupuesto;
CREATE UNIQUE INDEX composicion_orden_en_el_presupuesto ON composicion (padre_id, orden) WHERE version_id IS NULL AND baja_carga_id IS NULL;

CREATE TABLE renglon_historia (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    renglon_id  bigint NOT NULL REFERENCES composicion,
    carga_id    bigint NOT NULL REFERENCES carga,
    campo       text   NOT NULL CHECK (campo IN ('alta', 'cantidad', 'orden', 'baja')),
    antes       text,
    despues     text,
    creada_en   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX renglon_historia_del_renglon ON renglon_historia (renglon_id, id);

CREATE FUNCTION renglon_historia_solo_se_agrega() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'la historia de un renglón no se reescribe ni se borra: un cambio nuevo es una fila nueva';
END $$;

CREATE TRIGGER renglon_historia_solo_se_agrega BEFORE UPDATE OR DELETE ON renglon_historia
    FOR EACH ROW EXECUTE FUNCTION renglon_historia_solo_se_agrega();
