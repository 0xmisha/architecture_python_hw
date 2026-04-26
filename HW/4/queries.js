// ============================================================
// Hotel Booking System — MongoDB Queries (Variant 13)
// Run in mongosh: load("queries.js")
// ============================================================

use("hotel_booking");

// ============================================================
// USERS
// ============================================================

// --- 1. Создание нового пользователя ---
db.users.insertOne({
  login:         "new_user",
  password_hash: "$2b$12$...",
  first_name:    "Новый",
  last_name:     "Пользователь",
  email:         "new_user@example.com",
  created_at:    new Date()
});

// --- 2. Поиск пользователя по логину (точное совпадение) ---
db.users.findOne({ login: "ivan_petrov" });

// --- 3. Поиск пользователя по маске имя/фамилия (regex, case-insensitive) ---
db.users.find({
  $or: [
    { first_name: { $regex: "ван", $options: "i" } },
    { last_name:  { $regex: "ван", $options: "i" } }
  ]
});

// Альтернатива — полнотекстовый индекс (быстрее на больших коллекциях):
db.users.find({ $text: { $search: "Иван" } });

// ============================================================
// HOTELS
// ============================================================

// --- 4. Создание отеля ---
db.hotels.insertOne({
  name:            "Новый Отель",
  city:            "Москва",
  address:         "ул. Примерная, 1",
  stars:           4,
  rooms_total:     100,
  price_per_night: 7500,
  amenities:       ["WiFi", "Парковка"],
  created_at:      new Date()
});

// --- 5. Получение списка всех отелей ---
db.hotels.find({}).sort({ city: 1, name: 1 });

// --- 6. Поиск отелей по городу (case-insensitive) ---
db.hotels.find({
  city: { $regex: "осква", $options: "i" }
}).sort({ stars: -1, price_per_night: 1 });

// Поиск по точному совпадению города (быстрее с индексом):
db.hotels.find({ city: "Москва" }).sort({ stars: -1 });

// Дополнительно: фильтр по минимальной звёздности
db.hotels.find({
  city:  { $regex: "осква", $options: "i" },
  stars: { $gte: 4 }
});

// ============================================================
// BOOKINGS
// ============================================================

// --- 7. Создание бронирования ---
// Сначала получаем отель для snapshot
const hotel = db.hotels.findOne({ _id: ObjectId("222222222222222222222201") });
const nights = 3;
db.bookings.insertOne({
  user_id:  ObjectId("111111111111111111111101"),
  hotel_id: hotel._id,
  hotel_snapshot: {
    name:            hotel.name,
    city:            hotel.city,
    price_per_night: hotel.price_per_night
  },
  check_in:    new Date("2026-02-01"),
  check_out:   new Date("2026-02-04"),
  nights:      nights,
  total_price: nights * hotel.price_per_night,
  status:      "confirmed",
  created_at:  new Date()
});

// --- 8. Получение бронирований пользователя ---
db.bookings.find({
  user_id: ObjectId("111111111111111111111101")
}).sort({ created_at: -1 });

// Только активные (confirmed):
db.bookings.find({
  user_id: ObjectId("111111111111111111111101"),
  status:  "confirmed"
}).sort({ check_in: 1 });

// --- 9. Отмена бронирования ---
db.bookings.updateOne(
  {
    _id:     ObjectId("..."),   // id бронирования
    user_id: ObjectId("111111111111111111111101"),
    status:  { $ne: "cancelled" }
  },
  { $set: { status: "cancelled" } }
);

// --- 10. Получение бронирования по id (с проверкой владельца) ---
db.bookings.findOne({
  _id:     ObjectId("..."),
  user_id: ObjectId("111111111111111111111101")
});

// ============================================================
// РАЗНЫЕ ОПЕРАТОРЫ
// ============================================================

// $in — отели 4 или 5 звёзд
db.hotels.find({ stars: { $in: [4, 5] } });

// $gt / $lt — отели в ценовом диапазоне
db.hotels.find({
  price_per_night: { $gte: 5000, $lte: 15000 }
});

// $and — отель в Москве И >= 4 звезды И есть бассейн
db.hotels.find({
  $and: [
    { city:  "Москва" },
    { stars: { $gte: 4 } },
    { amenities: { $in: ["Бассейн"] } }
  ]
});

// $or — отели в Москве или Санкт-Петербурге
db.hotels.find({
  $or: [
    { city: "Москва" },
    { city: "Санкт-Петербург" }
  ]
});

// $ne — все бронирования кроме отменённых
db.bookings.find({ status: { $ne: "cancelled" } });

// Массивы: добавить удобство к отелю ($push)
db.hotels.updateOne(
  { _id: ObjectId("222222222222222222222201") },
  { $push: { amenities: "Кальян" } }
);

// Массивы: убрать удобство ($pull)
db.hotels.updateOne(
  { _id: ObjectId("222222222222222222222201") },
  { $pull: { amenities: "Кальян" } }
);

// Массивы: добавить без дублей ($addToSet)
db.hotels.updateOne(
  { _id: ObjectId("222222222222222222222201") },
  { $addToSet: { amenities: "Трансфер" } }
);

// ============================================================
// AGGREGATION PIPELINE
// ============================================================

// Выручка и количество активных броней по городам
db.bookings.aggregate([
  { $match: { status: "confirmed" } },
  {
    $group: {
      _id:              "$hotel_snapshot.city",
      active_bookings:  { $sum: 1 },
      total_revenue:    { $sum: "$total_price" },
      avg_stay_nights:  { $avg: "$nights" }
    }
  },
  {
    $project: {
      city:            "$_id",
      active_bookings: 1,
      total_revenue:   1,
      avg_stay_nights: { $round: ["$avg_stay_nights", 1] },
      _id:             0
    }
  },
  { $sort: { total_revenue: -1 } }
]);

// Топ-5 популярных отелей по числу броней
db.bookings.aggregate([
  { $match: { status: "confirmed" } },
  {
    $group: {
      _id:          "$hotel_id",
      hotel_name:   { $first: "$hotel_snapshot.name" },
      bookings_cnt: { $sum: 1 },
      revenue:      { $sum: "$total_price" }
    }
  },
  { $sort: { bookings_cnt: -1 } },
  { $limit: 5 },
  {
    $project: {
      _id:          0,
      hotel_name:   1,
      bookings_cnt: 1,
      revenue:      1
    }
  }
]);
