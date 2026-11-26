// =====================================================================
//  RPG Manager · Persistencia (semanas 7-10) · ajuste de MongoDB
//  Ejecutar en mongosh DESPUÉS de rpg_manager_mongo_seed.js (el de la nivelación).
//  Es el equivalente en MongoDB de alter_persistencia.sql.
//
//  Decisión de diseño: en el seed la precisión del Arquero está como fracción
//  (0.72), pero en MariaDB y en el modelo es un entero de 0 a 100 (72).
//  Este script la pasa a la misma escala para que los dos motores guarden
//  el dato igual.
//
//  También crea la colección items (el catálogo de ítems), que el
//  repositorio necesita para agregar ítems al inventario.
//
//  Los índices y la colección contadores los crea el repositorio solo la
//  primera vez que arranca; aquí se crean también para poder revisarlos
//  en Compass antes de correr la app.
//  Se puede ejecutar varias veces sin error.
//  Derechos de autor © Francisco Cuéllar
// =====================================================================
db = db.getSiblingDB("rpg_manager");

// Todo va dentro de un bloque para poder pegarlo varias veces en la misma sesión
(function () {
    const arqueros = db.personajes.find({ precision: { $lt: 1 } }).toArray();
    arqueros.forEach(doc => {
    db.personajes.updateOne(
      { _id: doc._id },
      { $set: { precision: Math.round(doc.precision * 100) } }
    );
  });

  print("Arqueros ajustados: " + arqueros.length);

  // 2. Id numérico para cada personaje (como el AUTO_INCREMENT de MariaDB)
  let mayor = db.personajes.find({ id_personaje: { $exists: true } })
                           .sort({ id_personaje: -1 }).limit(1).toArray();
  let siguiente = mayor.length ? mayor[0].id_personaje : 0;
  const sinId = db.personajes.find({ id_personaje: { $exists: false } })
                             .sort({ _id: 1 }).toArray();
  sinId.forEach(doc => {
    siguiente += 1;
    db.personajes.updateOne({ _id: doc._id }, { $set: { id_personaje: siguiente } });
  });
  db.contadores.updateOne(
    { _id: "personajes" },
    { $max: { seq: siguiente } },
    { upsert: true }
  );

  // 3. Índices únicos: las mismas reglas que PRIMARY KEY y UNIQUE en MariaDB
  db.personajes.createIndex({ id_personaje: 1 }, { unique: true });
  db.personajes.createIndex({ nombre: 1 }, { unique: true });

  // 4. Catálogo de ítems: la colección items, igual a la tabla item de MariaDB.
  //    Al agregar un ítem al inventario, el repositorio copia de aquí su tipo y valor.
  const catalogo = [
    { nombre: "Espada larga",       tipo: "arma",     valor: 120,  peso: 3.5 },
    { nombre: "Hacha de guerra",    tipo: "arma",     valor: 200,  peso: 5.0 },
    { nombre: "Báculo arcano",      tipo: "arma",     valor: 250,  peso: 2.0 },
    { nombre: "Arco élfico",        tipo: "arma",     valor: 180,  peso: 1.5 },
    { nombre: "Cota de malla",      tipo: "armadura", valor: 300,  peso: 12.0 },
    { nombre: "Túnica encantada",   tipo: "armadura", valor: 220,  peso: 1.0 },
    { nombre: "Poción de vida",     tipo: "pocion",   valor: 25,   peso: 0.3 },
    { nombre: "Elixir de maná",     tipo: "pocion",   valor: 40,   peso: 0.3 },
    { nombre: "Amuleto del dragón", tipo: "reliquia", valor: 1000, peso: 0.2 }
  ];
  catalogo.forEach(item => {
    db.items.updateOne({ nombre: item.nombre }, { $set: item }, { upsert: true });
  });
  db.items.createIndex({ nombre: 1 }, { unique: true });
  print("Ítems en el catálogo: " + db.items.countDocuments());

  // Verificación: Magos con mana y Arqueros con precisión, en orden de id
  db.personajes.find({}, { _id: 0, id_personaje: 1, nombre: 1, clase: 1, mana: 1, precision: 1 })
               .sort({ id_personaje: 1 })
               .forEach(printjson);
  printjson(db.contadores.findOne({ _id: "personajes" }));
})();