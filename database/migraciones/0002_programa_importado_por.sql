-- 0002 · Quién subió el programa
--
-- Importar un programa es lo más estructural que se hace sobre él (`1-mundo/PROGRAMA-CPM.md` §4.8): igual que
-- toda edición dice quién la hizo, el programa dice quién lo subió y con qué rol. Son opcionales a propósito:
-- los programas que se cargan desde el repositorio —las pruebas y `python3 -m api.servir`— no tienen quién, y
-- no se inventa uno. Lo que sí se exige: si se dice uno, que no sea vacío.

ALTER TABLE programa
    ADD COLUMN importado_por      text CHECK (importado_por <> ''),
    ADD COLUMN importado_con_rol  text CHECK (importado_con_rol <> ''),
    ADD CONSTRAINT programa_importado_completo CHECK ((importado_por IS NULL) = (importado_con_rol IS NULL));
