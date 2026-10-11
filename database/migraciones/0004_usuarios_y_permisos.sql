-- 0004 · Quién es cada quien y qué puede hacer
--
-- `1-mundo/MODELO.md` §5b: quién puede qué es una tabla (`ROL_FUNCION`), no una regla de código, para poder corregirla
-- sin tocar esquema. Aquí está esa tabla, con `USUARIO` y `USUARIO_ROL` (B-74): una persona puede tener más de un
-- rol, y se le encuentra por su correo, que es lo que entrega el proveedor de identidad (`api/autenticacion.py`).
--
-- Se siembran los seis roles y solo las dos funciones que hoy tienen código detrás (`editar_estructura_programa` y
-- `editar_fechas_programa`, con quién las tiene según §5b). Las demás de las treinta y cuatro se agregan cuando haya
-- un módulo que las use: este cerebro no asigna sin un caso. `ROL.clave` es nueva: es el nombre de máquina del rol.

CREATE TABLE rol (
    id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave   text NOT NULL UNIQUE CHECK (clave <> ''),
    nombre  text NOT NULL CHECK (nombre <> '')
);

CREATE TABLE funcion_atomica (
    id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave  text NOT NULL UNIQUE CHECK (clave <> '')
);

-- muchos a muchos, no disjunto: la misma función puede estar en varios roles (D-205)
CREATE TABLE rol_funcion (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rol_id      bigint NOT NULL REFERENCES rol,
    funcion_id  bigint NOT NULL REFERENCES funcion_atomica,
    UNIQUE (rol_id, funcion_id)
);

CREATE TABLE usuario (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre     text NOT NULL CHECK (nombre <> ''),
    correo     text NOT NULL CHECK (correo = lower(correo) AND position('@' in correo) > 1),
    activo     boolean NOT NULL DEFAULT true,   -- se retira, no se borra: su nombre sigue en la bitácora
    creado_en  timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX usuario_correo_unico ON usuario (correo);

CREATE TABLE usuario_rol (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id  bigint NOT NULL REFERENCES usuario,
    rol_id      bigint NOT NULL REFERENCES rol,
    UNIQUE (usuario_id, rol_id)
);

INSERT INTO rol (clave, nombre) VALUES
    ('residente', 'Residente'),
    ('supervisor', 'Supervisor'),
    ('superintendente', 'Superintendente'),
    ('costos', 'Costos'),
    ('cotizador', 'Cotizador'),
    ('control_de_obra', 'Control de obra');

INSERT INTO funcion_atomica (clave) VALUES ('editar_estructura_programa'), ('editar_fechas_programa');

INSERT INTO rol_funcion (rol_id, funcion_id)
SELECT r.id, f.id FROM (VALUES
    ('control_de_obra', 'editar_estructura_programa'),
    ('residente', 'editar_fechas_programa')
) AS a (rol, funcion)
JOIN rol r ON r.clave = a.rol
JOIN funcion_atomica f ON f.clave = a.funcion;
