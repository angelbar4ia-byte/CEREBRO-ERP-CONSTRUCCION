-- 0010 · La bandeja: propuestas y alertas
--
-- `1-mundo/CONOCIMIENTO.md` §14, `MODELO.md` §5 y §5a, `2-operacion/WORKFLOWS.md` §3 y §4, D-485.
--
-- «El sistema propone y el humano decide» aparecía nueve veces; sin una bandeja única, quien decide tendría nueve y el agente
-- interno no tendría dónde dejar lo que propone. Aquí vive.
--
-- - **PROPUESTA:** sugiere un valor para un objeto, con su evidencia. Una persona o el agente la deja; otra persona la aprueba
--   o la rechaza. **Una propuesta rechazada no se borra** (es lo que evita que se vuelva a proponer lo mismo) y **quien la propuso
--   no la aprueba** (D-269).
-- - **ALERTA:** señala algo que no cuadra y no sugiere ningún valor. Si reaparece sin haberse resuelto, sube `veces_vista`: es lo que
--   contesta «¿esto ya salió antes?». Nunca se resuelve sola.
--
-- `tipo` es abierto —crece igual que `PROPUESTA.tipo`—: lo valida el servicio contra los tipos que conoce, no la base, para que
-- agregar uno no sea una migración. `objeto` es la clave, la ruta o el prefijo sobre el que recae (texto), no una llave foránea:
-- una corrección de prefijo no recae en un nodo.

CREATE TABLE propuesta (
    id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo              text   NOT NULL CHECK (tipo <> ''),
    objeto            text   NOT NULL CHECK (objeto <> ''),
    valor_propuesto   jsonb  NOT NULL,                                -- la forma cambia según `tipo`
    evidencia         text   NOT NULL CHECK (btrim(evidencia) <> ''), -- una propuesta sin evidencia es una orden disfrazada
    origen            text   NOT NULL CHECK (origen IN ('usuario', 'agente')),
    modelo            text,                                           -- qué motor la produjo; solo si origen = agente
    version_modelo    text,
    confianza         text   CHECK (confianza IN ('alta', 'media', 'baja')),  -- se deriva de la evidencia; solo la trae un agente
    supuestos         jsonb,                                          -- solo si la respuesta proyecta a futuro
    base              bigint CHECK (base >= 0),                       -- la última carga que vio quien propuso: viaja a la aplicación
    propuesto_por     text   NOT NULL CHECK (propuesto_por <> ''),    -- el correo; del agente, su nombre
    propuesto_con_rol text   NOT NULL CHECK (propuesto_con_rol <> ''),
    creada_en         timestamptz NOT NULL DEFAULT now(),
    estado            text   NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'aprobada', 'rechazada')),
    resuelto_por      text,
    resuelto_con_rol  text,
    resuelta_en       timestamptz,
    nota              text,                                           -- por qué; obligatoria al rechazar
    resultado         jsonb,                                          -- lo que hizo el sistema al aprobarla
    CHECK (origen = 'agente' OR (modelo IS NULL AND version_modelo IS NULL AND confianza IS NULL AND supuestos IS NULL)),
    CHECK (origen = 'usuario' OR modelo IS NOT NULL),
    CHECK ((estado = 'pendiente') = (resuelto_por IS NULL)),
    CHECK (estado = 'pendiente' OR (resuelto_por <> '' AND resuelto_con_rol <> '' AND resuelta_en IS NOT NULL)),
    CHECK (estado = 'pendiente' OR resuelto_con_rol IS NOT NULL),
    CHECK (estado <> 'rechazada' OR btrim(coalesce(nota, '')) <> ''),
    CHECK (estado <> 'aprobada' OR lower(resuelto_por) <> lower(propuesto_por)),   -- quien propone no se aprueba
    CHECK (estado <> 'aprobada' OR resultado IS NOT NULL)
);
CREATE INDEX propuesta_por_estado ON propuesta (estado, tipo, id);
CREATE INDEX propuesta_del_objeto ON propuesta (tipo, objeto);

-- Una propuesta se resuelve una vez y queda como quedó: ni se reescribe ni se borra. Mientras está pendiente, lo único que cambia
-- es que alguien la resuelva.
CREATE FUNCTION propuesta_solo_se_resuelve() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'UPDATE'
       AND OLD.estado = 'pendiente' AND NEW.estado IN ('aprobada', 'rechazada')
       AND NEW.id = OLD.id AND NEW.tipo = OLD.tipo AND NEW.objeto = OLD.objeto AND NEW.valor_propuesto = OLD.valor_propuesto
       AND NEW.evidencia = OLD.evidencia AND NEW.origen = OLD.origen
       AND NEW.modelo IS NOT DISTINCT FROM OLD.modelo AND NEW.version_modelo IS NOT DISTINCT FROM OLD.version_modelo
       AND NEW.confianza IS NOT DISTINCT FROM OLD.confianza AND NEW.supuestos IS NOT DISTINCT FROM OLD.supuestos
       AND NEW.base IS NOT DISTINCT FROM OLD.base AND NEW.propuesto_por = OLD.propuesto_por
       AND NEW.propuesto_con_rol = OLD.propuesto_con_rol AND NEW.creada_en = OLD.creada_en THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'una propuesta no se reescribe ni se borra: solo se resuelve una vez, y lo rechazado se conserva';
END $$;

CREATE TRIGGER propuesta_solo_se_resuelve BEFORE UPDATE OR DELETE ON propuesta
    FOR EACH ROW EXECUTE FUNCTION propuesta_solo_se_resuelve();

CREATE TABLE alerta (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo             text   NOT NULL CHECK (tipo <> ''),
    objeto           text   NOT NULL DEFAULT '',                      -- a qué aplica; vacío si no hay un objeto al que apuntar
    evidencia        jsonb  NOT NULL,                                 -- qué se comparó, con qué método y qué dio
    parametro_usado  jsonb,                                           -- el umbral que la disparó, para ajustarlo sin tocar código
    primera_vez      timestamptz NOT NULL DEFAULT now(),
    ultima_vez       timestamptz NOT NULL DEFAULT now(),
    veces_vista      integer NOT NULL DEFAULT 1 CHECK (veces_vista >= 1),
    estado           text   NOT NULL DEFAULT 'activa' CHECK (estado IN ('activa', 'resuelta', 'descartada')),
    resuelto_por     text,
    resuelto_con_rol text,
    resuelta_en      timestamptz,
    nota_resolucion  text,                                            -- qué era: lo que alguien decidió al mirarla
    CHECK (ultima_vez >= primera_vez),
    CHECK ((estado = 'activa') = (resuelto_por IS NULL)),
    CHECK (estado = 'activa' OR (resuelto_por <> '' AND resuelto_con_rol <> '' AND resuelta_en IS NOT NULL AND btrim(coalesce(nota_resolucion, '')) <> ''))
);
-- La misma alerta (tipo y objeto) mientras no se resuelve es una sola fila: reaparecer la cuenta, no la repite.
CREATE UNIQUE INDEX alerta_una_activa ON alerta (tipo, objeto) WHERE estado = 'activa';
CREATE INDEX alerta_por_estado ON alerta (estado, tipo, id);

-- Una alerta activa solo recoge lo que vuelve a verse (la evidencia de hoy, la última vez, una vez más); resolverla cierra su
-- historia. Ni se borra ni se reescribe.
CREATE FUNCTION alerta_solo_se_cuenta_y_se_resuelve() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND OLD.estado = 'activa'
       AND NEW.id = OLD.id AND NEW.tipo = OLD.tipo AND NEW.objeto = OLD.objeto AND NEW.primera_vez = OLD.primera_vez THEN
        IF NEW.estado = 'activa' AND NEW.veces_vista >= OLD.veces_vista THEN
            RETURN NEW;
        END IF;
        IF NEW.estado IN ('resuelta', 'descartada') AND NEW.evidencia = OLD.evidencia
           AND NEW.parametro_usado IS NOT DISTINCT FROM OLD.parametro_usado AND NEW.ultima_vez = OLD.ultima_vez
           AND NEW.veces_vista = OLD.veces_vista THEN
            RETURN NEW;
        END IF;
    END IF;
    RAISE EXCEPTION 'una alerta no se borra: se cuenta cada vez que reaparece y se resuelve una vez';
END $$;

CREATE TRIGGER alerta_solo_se_cuenta_y_se_resuelve BEFORE UPDATE OR DELETE ON alerta
    FOR EACH ROW EXECUTE FUNCTION alerta_solo_se_cuenta_y_se_resuelve();

-- Quién resuelve la bandeja: dos funciones de `MODELO.md` §5b que existían desde P-21 sin dueño. Propuesta (D-485), corregible en la
-- tabla sin tocar esquema: `aprobar_propuesta` resuelve la bandeja (no aplica: aplicar pide la función de la acción) para Control de
-- obra, que ya gobierna entre obras; `resolver_alerta`, para Supervisor, que da seguimiento hasta el cierre, y Control de obra.
INSERT INTO funcion_atomica (clave) VALUES ('aprobar_propuesta'), ('resolver_alerta');

INSERT INTO rol_funcion (rol_id, funcion_id)
SELECT r.id, f.id FROM (VALUES
    ('control_de_obra', 'aprobar_propuesta'),
    ('supervisor', 'resolver_alerta'),
    ('control_de_obra', 'resolver_alerta')
) AS a (rol, funcion)
JOIN rol r ON r.clave = a.rol
JOIN funcion_atomica f ON f.clave = a.funcion;
