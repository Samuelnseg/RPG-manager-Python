// Archivo: db/mongo_persistencia.js (fragmento)

// 1. Precisión del Arquero: de fracción (0.72) a entero de 0 a 100 (72)
const arqueros = db.personajes.find({ precision: { $lt: 1 } }).toArray();
arqueros.forEach(doc => {
  db.personajes.updateOne(
    { _id: doc._id },
    { $set: { precision: Math.round(doc.precision * 100) } }
  );
});
print("Arqueros ajustados: " + arqueros.length);

// Archivo: db/consultas_repositorio.js (consulta 1)

// ── 1. Leer un personaje (buscarPorId) ───────────────────────────────
// La clase viaja dentro del documento: no hace falta ningún JOIN.
db.personajes.findOne(
  { id_personaje: 2 },
  { _id: 0, inventario: 0, misiones: 0 }
);

// Archivo: db/consultas_repositorio.js (consulta 2)

// ── 2. El inventario de un personaje (listarInventario) ──────────────
// El inventario es un arreglo embebido: se pide solo ese campo.
db.personajes.findOne(
  { id_personaje: 1 },
  { _id: 0, nombre: 1, inventario: 1 }
);

// Archivo: db/consultas_repositorio.js (consulta 3)

// ── 3. ¿Se puede borrar a Thorgar? (eliminar) ────────────────────────
// combates guarda NOMBRES, no llaves foráneas: nada impide el borrado.
db.combates.countDocuments({
  $or: [
    { atacante: "Thorgar" },
    { defensor: "Thorgar" },
    { ganador: "Thorgar" }
  ]
});
// Esta línea SÍ funciona en MongoDB (cuidado: deja combates huérfanos):
// db.personajes.deleteOne({ id_personaje: 1 });