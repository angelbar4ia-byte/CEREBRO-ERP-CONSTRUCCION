-- 0001 · El programa y la bitácora de lo que se edita
--
-- Primer corte de la persistencia del módulo de programa (`1-mundo/PROGRAMA-CPM.md` §4.7 y
-- `1-mundo/MODELO.md` §5c). Guarda el programa tal como se importa —filas con su `oid`, vínculos ya
-- resueltos por llave— y la bitácora de ediciones. Las fechas vigentes no se guardan: son la base más las
-- ediciones aplicadas, calculadas por el motor.
--
-- Todavía no cuelga de NODO, PRESUPUESTO ni CALENDARIO_OBRA (B-03: el árbol y el presupuesto aún no tienen
-- tabla). Cuando existan, `programa_fila` se vuelve ACTIVIDAD y TRAMO sin tocar la bitácora, que cita `oid`.
-- Los vínculos importados vienen sin `origen` declarado; los que alguien edita nunca quedan sin él.

CREATE TABLE programa (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    presupuesto_id  bigint,                          -- FK PRESUPUESTO cuando exista
    nombre          text        NOT NULL,
    calendario      jsonb       NOT NULL,            -- hasta que CALENDARIO_OBRA tenga su tabla
    version         integer     NOT NULL DEFAULT 0,  -- sube con cada edición o reversión: el candado contra editores simultáneos
    creado_en       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE programa_fila (
    programa_id  bigint   NOT NULL REFERENCES programa ON DELETE CASCADE,
    oid          text     NOT NULL,                  -- la llave estable: sobrevive a que se inserten filas (D-442)
    orden        integer  NOT NULL,                  -- posición en el libro
    fila         integer  NOT NULL,                  -- número de fila del libro: solo para citar el origen
    nivel        smallint NOT NULL,
    tipo         text     NOT NULL CHECK (tipo IN ('Capítulo', 'Subcapítulo', 'Nivel 2', 'Nivel 3', 'Concepto')),
    clave        text     NOT NULL,
    descripcion  text     NOT NULL,
    inicio       date,
    termino      date,
    dias         numeric  NOT NULL DEFAULT 0,
    frente       text     NOT NULL DEFAULT '',
    etapa        text     NOT NULL DEFAULT '',
    PRIMARY KEY (programa_id, oid),
    UNIQUE (programa_id, orden),
    UNIQUE (programa_id, fila),
    CHECK ((inicio IS NULL) = (termino IS NULL)),
    CHECK (inicio IS NULL OR termino >= inicio)
);

-- PRECEDENCIA (`MODELO.md` §5c): la sucesora siempre es una partida y la predecesora, una partida o un
-- bloque con partidas; eso lo valida quien carga, no la tabla. Un vínculo rechazado al cargar se queda aquí,
-- con su motivo, para que lo vea el planeador.
CREATE TABLE programa_vinculo (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,   -- el orden de inserción es el orden del libro
    programa_id      bigint  NOT NULL REFERENCES programa ON DELETE CASCADE,
    predecesora_oid  text,
    sucesora_oid     text    NOT NULL,
    tipo_vinculo     text    CHECK (tipo_vinculo IN ('fin_inicio', 'inicio_inicio', 'fin_fin', 'inicio_fin')),
    traslape_espera  numeric NOT NULL DEFAULT 0,     -- días hábiles; negativo es traslape, positivo es espera
    origen           text    CHECK (origen IN ('tecnica', 'recurso', 'decision')),
    confianza        text    GENERATED ALWAYS AS (
                         CASE origen WHEN 'tecnica' THEN 'alta' WHEN 'recurso' THEN 'media' WHEN 'decision' THEN 'baja' END
                     ) STORED,                       -- derivada del origen, no declarada
    estado           text    NOT NULL DEFAULT 'vigente' CHECK (estado IN ('vigente', 'rechazado')),
    motivo           text,
    texto_fuente     text,                           -- el token tal como venía en el libro
    FOREIGN KEY (programa_id, predecesora_oid) REFERENCES programa_fila (programa_id, oid),
    FOREIGN KEY (programa_id, sucesora_oid)    REFERENCES programa_fila (programa_id, oid),
    CHECK (
        (estado = 'vigente'   AND predecesora_oid IS NOT NULL AND tipo_vinculo IS NOT NULL AND motivo IS NULL)
        OR
        (estado = 'rechazado' AND motivo IS NOT NULL)
    )
);
CREATE INDEX programa_vinculo_sucesora ON programa_vinculo (programa_id, sucesora_oid);

-- La bitácora: cada edición que se aplicó, quién la hizo y qué vio al decidir. Solo se agrega; lo único
-- que cambia en una fila es pasar de `aplicada` a `revertida`.
CREATE TABLE edicion_programa (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    programa_id    bigint      NOT NULL REFERENCES programa ON DELETE CASCADE,
    secuencia      integer     NOT NULL,
    edicion        text        NOT NULL CHECK (edicion IN
                       ('cambiar_duracion', 'fijar_inicio', 'agregar_vinculo', 'quitar_vinculo', 'cambiar_vinculo')),
    datos          jsonb       NOT NULL,              -- la edición tal como se pidió, citando `oid`
    origen         text        CHECK (origen IN ('tecnica', 'recurso', 'decision')),   -- de los vínculos que agrega o cambia
    rol            text        NOT NULL,
    usuario        text        NOT NULL CHECK (usuario <> ''),
    estado         text        NOT NULL DEFAULT 'aplicada' CHECK (estado IN ('aplicada', 'revertida')),
    impacto        jsonb       NOT NULL,              -- lo que el sistema mostró al decidir
    creada_en      timestamptz NOT NULL DEFAULT now(),
    revertida_en   timestamptz,
    revertida_por  text,
    UNIQUE (programa_id, secuencia),
    CHECK ((estado = 'revertida') = (revertida_en IS NOT NULL AND revertida_por IS NOT NULL)),
    CHECK ((edicion IN ('agregar_vinculo', 'cambiar_vinculo')) = (origen IS NOT NULL))
);

CREATE FUNCTION edicion_programa_solo_se_agrega() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'la bitácora de ediciones no se borra';
    END IF;
    IF OLD.estado = 'aplicada' AND NEW.estado = 'revertida'
       AND NEW.id = OLD.id AND NEW.programa_id = OLD.programa_id AND NEW.secuencia = OLD.secuencia
       AND NEW.edicion = OLD.edicion AND NEW.datos = OLD.datos AND NEW.rol = OLD.rol
       AND NEW.usuario = OLD.usuario AND NEW.impacto = OLD.impacto AND NEW.creada_en = OLD.creada_en
       AND NEW.origen IS NOT DISTINCT FROM OLD.origen THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'una edición aplicada solo puede pasar a revertida';
END;
$$;

CREATE TRIGGER edicion_programa_bitacora
    BEFORE UPDATE OR DELETE ON edicion_programa
    FOR EACH ROW EXECUTE FUNCTION edicion_programa_solo_se_agrega();
