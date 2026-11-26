// =====================================================================
//  RPG Manager · Las consultas que ejecuta RepositorioMongo
//  Pégalas en mongosh (Compass o Atlas) para ver qué hace tu repositorio
//  por dentro. Requiere rpg_manager_mongo_seed.js y mongo_persistencia.js.
//  Derechos de autor © Francisco Cuéllar
// =====================================================================
db = db.getSiblingDB("rpg_manager");

db.personajes.findOne(
  { id_personaje: 2 },
  { _id: 0, inventario: 0, misiones: 0 }
);

db.personajes.findOne(
  { id_personaje: 1 },
  { _id: 0, nombre: 1, inventario: 1 }
);

db.combates.countDocuments({
  $or: [
    { atacante: "Thorgar" },
    { defensor: "Thorgar" },
    { ganador: "Thorgar" }
  ]
});


// ── 4. Sumar un ítem al inventario (agregarItem) ─────────────────────
// Paso 1: si ya lo tiene, $inc sobre ese elemento del arreglo.
const resultado = db.personajes.updateOne(
  { id_personaje: 7, "inventario.item": "Poción de vida" },
  { $inc: { "inventario.$.cantidad": 2 } }
);
// Paso 2: si no lo tenía, se copia del catálogo y se agrega con $push.
if (resultado.matchedCount === 0) {
  const delCatalogo = db.items.findOne({ nombre: "Poción de vida" });
  db.personajes.updateOne(
    { id_personaje: 7 },
    { $push: { inventario: { item: delCatalogo.nombre, tipo: delCatalogo.tipo,
                             valor: delCatalogo.valor, cantidad: 2 } } }
  );
}