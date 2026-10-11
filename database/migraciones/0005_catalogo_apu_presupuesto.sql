-- 0005 · El catálogo de insumos, las matrices (APU) con su versionado, y los presupuestos
--
-- `1-mundo/MODELO.md` §1 (NODO), §1a (COMPOSICION), §3 (PRESUPUESTO) y §4 y §4a (VERSION_CONCEPTO, PRECIO_HISTORICO), con
-- los archivos de OPUS que sí hay en `1-mundo/opus/`. Lo escribe `backend/infra/postgres_catalogo.py` y solo se agrega:
-- lo que cambia, cambia con una versión nueva o con un precio nuevo, no con un UPDATE.
--
-- Cuatro decisiones del modelo que aquí se hacen concretas (D-473):
--
-- 1. **La matriz es de una versión.** `MODELO.md` ligaba `COMPOSICION` al nodo, pero también pedía que una matriz que
--    cambia deje la anterior intacta (§2.2 de `CONOCIMIENTO.md`: «Versión 1: insumos + cantidades + PU»). Las dos cosas
--    solo caben si cada línea dice a qué versión pertenece: `composicion.version_id`. La matriz vigente es la última.
--
-- 2. **El renglón de un presupuesto es una línea de COMPOSICION** del nodo estructural al concepto, con la cantidad de
--    esa obra, y **fija la versión** del concepto que tenía al cargarse (`hijo_version_id`): «el renglón apunta a una
--    versión concreta, no a la clave suelta». Así el mismo concepto está en muchos lugares sin repetirse, y 58 cantidades
--    negativas, que son de la línea y no del nodo, tienen dónde vivir.
--
-- 3. **Los nodos estructurales (capítulo, subcapítulo, nivel) son de un presupuesto**, no del catálogo: `ECO-00001` está
--    en los siete prototipos con hijos distintos. Su identidad es la ruta natural —clave y lugar entre las del mismo
--    nombre— dentro del presupuesto (`CONOCIMIENTO.md` §2.3: «clave, y ruta o prototipo para los estructurales»). La clave
--    es única solo entre los nodos del catálogo.
--
-- 4. **La unidad puede no saberse.** `MODELO.md` la pide obligatoria, pero ni las 39 cuadrillas ni un concepto que no cuelga
--    de ningún presupuesto traen unidad en los archivos que hay, y el catálogo de unidades no está. Se guarda lo que
--    viene; `unidad_id` es nulo hasta que se sepa.

CREATE TABLE unidad (
    id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave   text NOT NULL CHECK (clave <> '' AND clave = btrim(clave)),   -- tal como vino la primera vez
    nombre  text                                                          -- «Metro Cuadrado», cuando se tenga el catálogo
);
-- «pza» y «PZ» no se juntan: no se sabe que sean la misma unidad. «serv» y «SERV» sí: solo cambia la mayúscula.
CREATE UNIQUE INDEX unidad_clave_unica ON unidad (lower(clave));

-- Una carga es lo que se aplicó de un archivo de OPUS, por quién y qué quedó pendiente (`CONOCIMIENTO.md` §2.9).
CREATE TABLE carga (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    creada_en  timestamptz NOT NULL DEFAULT now(),
    usuario    text  NOT NULL CHECK (usuario <> ''),     -- el correo, como en la bitácora de ediciones (D-469)
    rol        text  NOT NULL CHECK (rol <> ''),
    archivos   jsonb NOT NULL,                           -- nombre → huella sha256 del contenido
    resumen    jsonb NOT NULL                            -- qué entró, qué versionó y qué quedó pendiente, con su motivo
);

CREATE TABLE presupuesto (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave       text NOT NULL CHECK (clave <> ''),       -- la del capítulo: es con lo que se reconoce al volver a cargar
    nombre      text NOT NULL,
    tipo        text NOT NULL CHECK (tipo IN ('plantilla', 'obra', 'escenario')),
    raiz_id     bigint,                                  -- FK nodo, abajo
    huella      text NOT NULL,                           -- de su estructura y cantidades: para saber si lo que llega es lo mismo
    carga_id    bigint NOT NULL REFERENCES carga,
    creado_en   timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX presupuesto_clave_unica ON presupuesto (clave);

CREATE TABLE nodo (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    presupuesto_id   bigint REFERENCES presupuesto,      -- solo los estructurales
    clave            text NOT NULL CHECK (clave <> ''),
    descripcion      text NOT NULL DEFAULT '',
    unidad_id        bigint REFERENCES unidad,
    rol              text NOT NULL CHECK (rol IN ('ensamble', 'concepto', 'insumo', 'estructural')),
    categoria        text NOT NULL CHECK (categoria IN
                         ('material', 'mano_de_obra', 'herramienta', 'equipo', 'auxiliar', 'flete', 'trabajo', 'concepto')),
    modo_precio      text NOT NULL DEFAULT 'calculado' CHECK (modo_precio IN ('calculado', 'declarado')),
    precio_declarado numeric,                            -- caché del precio vigente (precio_historico); nunca la fuente
    tipo_opus        text CHECK (tipo_opus IN ('Capítulo', 'Subcapítulo', 'Nivel 2', 'Nivel 3')),   -- solo estructurales
    ruta_natural     text,                               -- solo estructurales: clave#n/clave#n…
    procedencia      text NOT NULL DEFAULT 'importado' CHECK (procedencia IN
                         ('importado', 'manual', 'fusion', 'division', 'extraccion', 'composicion', 'clonacion')),
    CHECK ((rol = 'estructural') = (presupuesto_id IS NOT NULL)),
    CHECK ((rol = 'estructural') = (ruta_natural IS NOT NULL)),
    CHECK ((rol = 'estructural') = (tipo_opus IS NOT NULL)),
    CHECK (modo_precio <> 'declarado' OR precio_declarado IS NOT NULL)
);
CREATE UNIQUE INDEX nodo_clave_del_catalogo ON nodo (clave) WHERE rol <> 'estructural';
CREATE UNIQUE INDEX nodo_ruta_del_presupuesto ON nodo (presupuesto_id, ruta_natural) WHERE rol = 'estructural';

ALTER TABLE presupuesto ADD CONSTRAINT presupuesto_raiz FOREIGN KEY (raiz_id) REFERENCES nodo;

-- La receta (insumos y cantidades) con su precio congelado al crearse. Cualquier cambio en el conjunto de insumos o en sus
-- cantidades es una versión nueva, sin umbral (`CONOCIMIENTO.md` §2.2); la descripción y los precios no cuentan.
CREATE TABLE version_concepto (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nodo_id        bigint NOT NULL REFERENCES nodo,
    version        integer NOT NULL CHECK (version >= 1),
    vigente_desde  timestamptz NOT NULL DEFAULT now(),
    huella         text NOT NULL,
    pu             numeric NOT NULL,                     -- el PU de ese día; se congela, nunca se recalcula
    carga_id       bigint NOT NULL REFERENCES carga,
    UNIQUE (nodo_id, version),
    UNIQUE (id, nodo_id)
);

-- La tabla más importante del modelo (`MODELO.md` §1a): de aquí sale el cálculo completo. Las líneas de una matriz llevan
-- `version_id`; las de un presupuesto no, y fijan la versión del concepto en `hijo_version_id`.
CREATE TABLE composicion (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    padre_id         bigint  NOT NULL REFERENCES nodo,
    version_id       bigint,
    hijo_id          bigint  NOT NULL REFERENCES nodo,
    hijo_version_id  bigint,
    cantidad         numeric NOT NULL,                   -- puede ser negativa (58 casos) y repetirse el mismo hijo (26)
    orden            integer NOT NULL CHECK (orden >= 1),
    reporta_a        text    NOT NULL CHECK (reporta_a IN
                         ('material', 'mano_de_obra', 'herramienta', 'equipo', 'auxiliar', 'flete', 'trabajo', 'concepto')),
    tipo_cantidad    text    NOT NULL DEFAULT 'fija' CHECK (tipo_cantidad IN ('fija', 'porcentaje')),
    base_porcentaje  text    CHECK (base_porcentaje IN ('suma_jornales_hermanos', 'acumulado_hasta_aqui')),
    FOREIGN KEY (version_id, padre_id) REFERENCES version_concepto (id, nodo_id),
    FOREIGN KEY (hijo_version_id, hijo_id) REFERENCES version_concepto (id, nodo_id),
    CHECK ((tipo_cantidad = 'porcentaje') = (base_porcentaje IS NOT NULL)),
    CHECK (padre_id <> hijo_id),
    CHECK (version_id IS NULL OR hijo_version_id IS NULL)   -- una matriz no fija versiones: usa la vigente del hijo
);
CREATE UNIQUE INDEX composicion_orden_en_la_matriz ON composicion (version_id, orden) WHERE version_id IS NOT NULL;
CREATE UNIQUE INDEX composicion_orden_en_el_presupuesto ON composicion (padre_id, orden) WHERE version_id IS NULL;
CREATE INDEX composicion_hijo ON composicion (hijo_id);

-- El precio de un insumo tiene su historia aparte de la receta (`MODELO.md` §4a): que se mueva no crea versión de nada.
CREATE TABLE precio_historico (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nodo_id        bigint NOT NULL REFERENCES nodo,
    precio         numeric NOT NULL,
    vigente_desde  timestamptz NOT NULL DEFAULT now(),
    vigente_hasta  timestamptz,                          -- nulo: el vigente hoy
    fuente         text NOT NULL CHECK (fuente IN ('catalogo', 'ingenieria')),
    carga_id       bigint REFERENCES carga,
    CHECK (vigente_hasta IS NULL OR vigente_hasta >= vigente_desde)
);
CREATE UNIQUE INDEX precio_historico_un_vigente ON precio_historico (nodo_id) WHERE vigente_hasta IS NULL;

-- Nada de esto se reescribe: una versión o una línea de matriz que ya existe no cambia nunca, y un precio histórico solo
-- puede cerrarse (poner su `vigente_hasta`). Lo demás es agregar.
CREATE FUNCTION catalogo_solo_se_agrega() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION '% no se reescribe ni se borra: lo que cambia es una versión o un precio nuevo', TG_TABLE_NAME;
END $$;

CREATE FUNCTION precio_historico_solo_se_cierra() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'UPDATE'
       AND OLD.vigente_hasta IS NULL AND NEW.vigente_hasta IS NOT NULL
       AND NEW.id = OLD.id AND NEW.nodo_id = OLD.nodo_id AND NEW.precio = OLD.precio
       AND NEW.vigente_desde = OLD.vigente_desde AND NEW.fuente = OLD.fuente AND NEW.carga_id IS NOT DISTINCT FROM OLD.carga_id THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'un precio histórico solo se cierra: no se reescribe ni se borra; el precio nuevo es una fila nueva';
END $$;

CREATE TRIGGER version_concepto_solo_se_agrega BEFORE UPDATE OR DELETE ON version_concepto
    FOR EACH ROW EXECUTE FUNCTION catalogo_solo_se_agrega();
CREATE TRIGGER composicion_de_matriz_solo_se_agrega BEFORE UPDATE OR DELETE ON composicion
    FOR EACH ROW WHEN (OLD.version_id IS NOT NULL) EXECUTE FUNCTION catalogo_solo_se_agrega();
CREATE TRIGGER precio_historico_solo_se_cierra BEFORE UPDATE OR DELETE ON precio_historico
    FOR EACH ROW EXECUTE FUNCTION precio_historico_solo_se_cierra();
CREATE TRIGGER carga_solo_se_agrega BEFORE UPDATE OR DELETE ON carga
    FOR EACH ROW EXECUTE FUNCTION catalogo_solo_se_agrega();

-- Quién puede cargar: una función nueva de `MODELO.md` §5b, propuesta, para Control de obra y para Costos (quien cuantifica
-- y crea precios). Se corrige en la tabla, sin tocar esquema.
INSERT INTO funcion_atomica (clave) VALUES ('cargar_catalogo_opus');

INSERT INTO rol_funcion (rol_id, funcion_id)
SELECT r.id, f.id FROM (VALUES ('control_de_obra', 'cargar_catalogo_opus'), ('costos', 'cargar_catalogo_opus')) AS a (rol, funcion)
JOIN rol r ON r.clave = a.rol
JOIN funcion_atomica f ON f.clave = a.funcion;
