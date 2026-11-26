-- ─────────────────────────────────────────────────────────────────────
-- RPG Manager · Las consultas que ejecuta RepositorioMariaDB
-- Ejecútalas en HeidiSQL o en la consola para ver qué hace tu repositorio
-- por dentro. Requiere rpg_manager_schema.sql y alter_persistencia.sql.
-- Derechos de autor © Francisco Cuéllar
-- ─────────────────────────────────────────────────────────────────────
USE rpg_manager;

SELECT p.id_personaje, p.nombre, c.nombre AS clase,
       p.nivel, p.vida, p.ataque, p.oro, p.mana, p.precision_tiro
  FROM personaje p
  JOIN clase c ON p.id_clase = c.id_clase
 WHERE p.id_personaje = 2;


SELECT i.nombre, i.tipo, i.valor, inv.cantidad
  FROM inventario inv
  JOIN item i ON inv.id_item = i.id_item
 WHERE inv.id_personaje = 1
 ORDER BY i.nombre;


SELECT COUNT(*) AS combates_de_thorgar
  FROM combate
 WHERE id_atacante = 1
    OR id_defensor = 1
    OR id_ganador = 1;


-- ── 4. Sumar un ítem al inventario (agregarItem) ─────────────────────
-- Si la llave (id_personaje, id_item) ya existe, suma la cantidad.
INSERT INTO inventario (id_personaje, id_item, cantidad)
SELECT 7, id_item, 2 FROM item WHERE nombre = 'Poción de vida'
    ON DUPLICATE KEY UPDATE cantidad = inventario.cantidad + VALUES(cantidad);