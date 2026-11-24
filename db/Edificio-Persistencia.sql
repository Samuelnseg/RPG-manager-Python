-- Archivo: db/alter_persistencia.sql (fragmento)
ALTER TABLE personaje
  ADD COLUMN IF NOT EXISTS mana           INT NULL CHECK (mana >= 0),
  ADD COLUMN IF NOT EXISTS precision_tiro INT NULL CHECK (precision_tiro BETWEEN 0 AND 100);

-- Valores iniciales para los personajes que ya existían
UPDATE personaje p JOIN clase c ON p.id_clase = c.id_clase
   SET p.mana = 100
 WHERE c.nombre = 'Mago' AND p.mana IS NULL;

UPDATE personaje p JOIN clase c ON p.id_clase = c.id_clase
   SET p.precision_tiro = 70
 WHERE c.nombre = 'Arquero' AND p.precision_tiro IS NULL;


 -- Archivo: db/consultas_repositorio.sql (consulta 1)

-- ── 1. Leer un personaje (buscarPorId) ───────────────────────────────
-- La clase no está como texto en personaje: llega desde la tabla clase.
SELECT p.id_personaje, p.nombre, c.nombre AS clase,
       p.nivel, p.vida, p.ataque, p.oro, p.mana, p.precision_tiro
  FROM personaje p
  JOIN clase c ON p.id_clase = c.id_clase
 WHERE p.id_personaje = 2;

 -- Archivo: db/consultas_repositorio.sql (consulta 2)

-- ── 2. El inventario de un personaje (listarInventario) ──────────────
-- inventario es la tabla intermedia N:M: el nombre del ítem vive en item.
SELECT i.nombre, i.tipo, i.valor, inv.cantidad
  FROM inventario inv
  JOIN item i ON inv.id_item = i.id_item
 WHERE inv.id_personaje = 1
 ORDER BY i.nombre;

 -- Archivo: db/consultas_repositorio.sql (consulta 3)

-- ── 3. ¿Por qué no se puede borrar a Thorgar? (eliminar) ─────────────
-- combate apunta a personaje con tres llaves foráneas y sin CASCADE.
SELECT COUNT(*) AS combates_de_thorgar
  FROM combate
 WHERE id_atacante = 1
    OR id_defensor = 1
    OR id_ganador = 1;
-- Esta línea falla con el error 1451 (llave foránea en uso):
-- DELETE FROM personaje WHERE id_personaje = 1;