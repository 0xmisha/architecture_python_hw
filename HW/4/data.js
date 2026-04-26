// ============================================================
// Hotel Booking System — Test Data (Variant 13)
// Run in mongosh: load("data.js")  or  mongosh hotel_booking data.js
// ============================================================

use("hotel_booking");

// ------------------------------------------------------------
// Clear existing data
// ------------------------------------------------------------
db.users.drop();
db.hotels.drop();
db.bookings.drop();

// ------------------------------------------------------------
// Users  (password_hash == bcrypt("password123"))
// ------------------------------------------------------------
const u1  = ObjectId("111111111111111111111101");
const u2  = ObjectId("111111111111111111111102");
const u3  = ObjectId("111111111111111111111103");
const u4  = ObjectId("111111111111111111111104");
const u5  = ObjectId("111111111111111111111105");
const u6  = ObjectId("111111111111111111111106");
const u7  = ObjectId("111111111111111111111107");
const u8  = ObjectId("111111111111111111111108");
const u9  = ObjectId("111111111111111111111109");
const u10 = ObjectId("11111111111111111111110a");

db.users.insertMany([
  { _id: u1,  login: "ivan_petrov",    password_hash: "$2b$12$K8tTOHPbXVkRi0RTVB5VX.e8LJ0VObCGX6XjvqUuJg5v3oWfB5lDe", first_name: "Иван",    last_name: "Петров",   email: "ivan.petrov@mail.ru",    created_at: new Date("2024-01-10") },
  { _id: u2,  login: "maria_ivanova",  password_hash: "$2b$12$K8tTOHPbXVkRi0RTVB5VX.e8LJ0VObCGX6XjvqUuJg5v3oWfB5lDe", first_name: "Мария",   last_name: "Иванова",  email: "maria.ivanova@mail.ru",  created_at: new Date("2024-02-05") },
  { _id: u3,  login: "alex_smirnov",   password_hash: "$2b$12$K8tTOHPbXVkRi0RTVB5VX.e8LJ0VObCGX6XjvqUuJg5v3oWfB5lDe", first_name: "Алексей", last_name: "Смирнов",  email: "alex.smirnov@mail.ru",   created_at: new Date("2024-03-15") },
  { _id: u4,  login: "olga_novikova",  password_hash: "$2b$12$K8tTOHPbXVkRi0RTVB5VX.e8LJ0VObCGX6XjvqUuJg5v3oWfB5lDe", first_name: "Ольга",   last_name: "Новикова", email: "olga.novikova@mail.ru",  created_at: new Date("2024-04-01") },
  { _id: u5,  login: "dmitry_kozlov",  password_hash: "$2b$12$K8tTOHPbXVkRi0RTVB5VX.e8LJ0VObCGX6XjvqUuJg5v3oWfB5lDe", first_name: "Дмитрий", last_name: "Козлов",   email: "dmitry.kozlov@mail.ru",  created_at: new Date("2024-05-20") },
  { _id: u6,  login: "elena_morozova", password_hash: "$2b$12$K8tTOHPbXVkRi0RTVB5VX.e8LJ0VObCGX6XjvqUuJg5v3oWfB5lDe", first_name: "Елена",   last_name: "Морозова", email: "elena.morozova@mail.ru", created_at: new Date("2024-06-11") },
  { _id: u7,  login: "nikita_volkov",  password_hash: "$2b$12$K8tTOHPbXVkRi0RTVB5VX.e8LJ0VObCGX6XjvqUuJg5v3oWfB5lDe", first_name: "Никита",  last_name: "Волков",   email: "nikita.volkov@mail.ru",  created_at: new Date("2024-07-03") },
  { _id: u8,  login: "anna_sokolova",  password_hash: "$2b$12$K8tTOHPbXVkRi0RTVB5VX.e8LJ0VObCGX6XjvqUuJg5v3oWfB5lDe", first_name: "Анна",    last_name: "Соколова", email: "anna.sokolova@mail.ru",  created_at: new Date("2024-08-14") },
  { _id: u9,  login: "sergey_popov",   password_hash: "$2b$12$K8tTOHPbXVkRi0RTVB5VX.e8LJ0VObCGX6XjvqUuJg5v3oWfB5lDe", first_name: "Сергей",  last_name: "Попов",    email: "sergey.popov@mail.ru",   created_at: new Date("2024-09-22") },
  { _id: u10, login: "tatyana_lebed",  password_hash: "$2b$12$K8tTOHPbXVkRi0RTVB5VX.e8LJ0VObCGX6XjvqUuJg5v3oWfB5lDe", first_name: "Татьяна", last_name: "Лебедева", email: "tatyana.lebed@mail.ru",  created_at: new Date("2024-10-30") },
]);

// ------------------------------------------------------------
// Hotels
// ------------------------------------------------------------
const h1  = ObjectId("222222222222222222222201");
const h2  = ObjectId("222222222222222222222202");
const h3  = ObjectId("222222222222222222222203");
const h4  = ObjectId("222222222222222222222204");
const h5  = ObjectId("222222222222222222222205");
const h6  = ObjectId("222222222222222222222206");
const h7  = ObjectId("222222222222222222222207");
const h8  = ObjectId("222222222222222222222208");
const h9  = ObjectId("222222222222222222222209");
const h10 = ObjectId("22222222222222222222220a");
const h11 = ObjectId("22222222222222222222220b");
const h12 = ObjectId("22222222222222222222220c");

db.hotels.insertMany([
  { _id: h1,  name: "Marriott Москва",        city: "Москва",           address: "Тверская ул., 26",         stars: 5, rooms_total: 340,  price_per_night: 15000, amenities: ["WiFi", "Парковка", "Бассейн", "Спа", "Ресторан"], created_at: new Date("2020-01-01") },
  { _id: h2,  name: "Hilton Санкт-Петербург", city: "Санкт-Петербург",  address: "Невский пр., 57",          stars: 5, rooms_total: 280,  price_per_night: 12000, amenities: ["WiFi", "Ресторан", "Конференц-зал", "Спа"],       created_at: new Date("2020-02-01") },
  { _id: h3,  name: "Novotel Москва Сити",    city: "Москва",           address: "Пресненская наб., 2",      stars: 4, rooms_total: 360,  price_per_night: 9000,  amenities: ["WiFi", "Парковка", "Фитнес", "Ресторан"],          created_at: new Date("2020-03-01") },
  { _id: h4,  name: "Ibis Казань",            city: "Казань",           address: "ул. Баумана, 9",           stars: 3, rooms_total: 200,  price_per_night: 3500,  amenities: ["WiFi", "Завтрак"],                                 created_at: new Date("2020-04-01") },
  { _id: h5,  name: "Radisson Сочи",          city: "Сочи",             address: "ул. Орджоникидзе, 11",     stars: 4, rooms_total: 420,  price_per_night: 8000,  amenities: ["WiFi", "Бассейн", "Пляж", "Ресторан", "Спа"],     created_at: new Date("2020-05-01") },
  { _id: h6,  name: "Park Inn Екатеринбург",  city: "Екатеринбург",     address: "ул. Малышева, 128",        stars: 4, rooms_total: 170,  price_per_night: 5500,  amenities: ["WiFi", "Парковка", "Фитнес", "Ресторан"],          created_at: new Date("2020-06-01") },
  { _id: h7,  name: "Lotte Hotel Москва",     city: "Москва",           address: "Новинский б-р, 8",         stars: 5, rooms_total: 300,  price_per_night: 20000, amenities: ["WiFi", "Бассейн", "Спа", "Ресторан", "Барбershop"], created_at: new Date("2020-07-01") },
  { _id: h8,  name: "Гостиница Астория",      city: "Санкт-Петербург",  address: "Большая Морская ул., 39",  stars: 5, rooms_total: 168,  price_per_night: 18000, amenities: ["WiFi", "Ресторан", "Бар", "Спа"],                  created_at: new Date("2020-08-01") },
  { _id: h9,  name: "Mercure Нижний Новгород",city: "Нижний Новгород",  address: "ул. Заломова, 2",          stars: 4, rooms_total: 145,  price_per_night: 4800,  amenities: ["WiFi", "Завтрак", "Парковка"],                     created_at: new Date("2020-09-01") },
  { _id: h10, name: "Cosmos Hotel Москва",    city: "Москва",           address: "пр-т Мира, 150",           stars: 3, rooms_total: 1777, price_per_night: 3200,  amenities: ["WiFi", "Парковка", "Ресторан"],                    created_at: new Date("2020-10-01") },
  { _id: h11, name: "Domina Firence",         city: "Санкт-Петербург",  address: "Литейный пр., 46",         stars: 4, rooms_total: 107,  price_per_night: 7000,  amenities: ["WiFi", "Завтрак", "Ресторан"],                     created_at: new Date("2020-11-01") },
  { _id: h12, name: "Amaks Конгресс-Отель",   city: "Екатеринбург",     address: "ул. Хохрякова, 68",        stars: 3, rooms_total: 250,  price_per_night: 2900,  amenities: ["WiFi", "Парковка"],                                created_at: new Date("2020-12-01") },
]);

// ------------------------------------------------------------
// Bookings
// ------------------------------------------------------------
db.bookings.insertMany([
  { _id: ObjectId(), user_id: u1, hotel_id: h1,  hotel_snapshot: { name: "Marriott Москва",        city: "Москва",          price_per_night: 15000 }, check_in: new Date("2025-01-10"), check_out: new Date("2025-01-15"), nights: 5,  total_price: 75000,  status: "confirmed", created_at: new Date("2024-12-01") },
  { _id: ObjectId(), user_id: u1, hotel_id: h5,  hotel_snapshot: { name: "Radisson Сочи",          city: "Сочи",            price_per_night: 8000  }, check_in: new Date("2025-03-01"), check_out: new Date("2025-03-07"), nights: 6,  total_price: 48000,  status: "cancelled", created_at: new Date("2025-01-15") },
  { _id: ObjectId(), user_id: u2, hotel_id: h2,  hotel_snapshot: { name: "Hilton Санкт-Петербург", city: "Санкт-Петербург", price_per_night: 12000 }, check_in: new Date("2025-02-14"), check_out: new Date("2025-02-18"), nights: 4,  total_price: 48000,  status: "confirmed", created_at: new Date("2025-01-20") },
  { _id: ObjectId(), user_id: u2, hotel_id: h8,  hotel_snapshot: { name: "Гостиница Астория",      city: "Санкт-Петербург", price_per_night: 18000 }, check_in: new Date("2025-04-20"), check_out: new Date("2025-04-25"), nights: 5,  total_price: 90000,  status: "confirmed", created_at: new Date("2025-03-01") },
  { _id: ObjectId(), user_id: u3, hotel_id: h3,  hotel_snapshot: { name: "Novotel Москва Сити",    city: "Москва",          price_per_night: 9000  }, check_in: new Date("2025-05-01"), check_out: new Date("2025-05-04"), nights: 3,  total_price: 27000,  status: "confirmed", created_at: new Date("2025-03-10") },
  { _id: ObjectId(), user_id: u4, hotel_id: h7,  hotel_snapshot: { name: "Lotte Hotel Москва",     city: "Москва",          price_per_night: 20000 }, check_in: new Date("2025-06-15"), check_out: new Date("2025-06-20"), nights: 5,  total_price: 100000, status: "confirmed", created_at: new Date("2025-04-01") },
  { _id: ObjectId(), user_id: u5, hotel_id: h4,  hotel_snapshot: { name: "Ibis Казань",            city: "Казань",          price_per_night: 3500  }, check_in: new Date("2025-07-10"), check_out: new Date("2025-07-12"), nights: 2,  total_price: 7000,   status: "confirmed", created_at: new Date("2025-05-20") },
  { _id: ObjectId(), user_id: u6, hotel_id: h6,  hotel_snapshot: { name: "Park Inn Екатеринбург",  city: "Екатеринбург",    price_per_night: 5500  }, check_in: new Date("2025-08-05"), check_out: new Date("2025-08-10"), nights: 5,  total_price: 27500,  status: "confirmed", created_at: new Date("2025-06-01") },
  { _id: ObjectId(), user_id: u7, hotel_id: h9,  hotel_snapshot: { name: "Mercure Нижний Новгород",city: "Нижний Новгород", price_per_night: 4800  }, check_in: new Date("2025-09-01"), check_out: new Date("2025-09-03"), nights: 2,  total_price: 9600,   status: "cancelled", created_at: new Date("2025-07-10") },
  { _id: ObjectId(), user_id: u8, hotel_id: h10, hotel_snapshot: { name: "Cosmos Hotel Москва",    city: "Москва",          price_per_night: 3200  }, check_in: new Date("2025-10-10"), check_out: new Date("2025-10-15"), nights: 5,  total_price: 16000,  status: "confirmed", created_at: new Date("2025-08-01") },
  { _id: ObjectId(), user_id: u9, hotel_id: h11, hotel_snapshot: { name: "Domina Firence",         city: "Санкт-Петербург", price_per_night: 7000  }, check_in: new Date("2025-11-20"), check_out: new Date("2025-11-23"), nights: 3,  total_price: 21000,  status: "confirmed", created_at: new Date("2025-09-05") },
  { _id: ObjectId(), user_id: u10,hotel_id: h12, hotel_snapshot: { name: "Amaks Конгресс-Отель",   city: "Екатеринбург",    price_per_night: 2900  }, check_in: new Date("2025-12-01"), check_out: new Date("2025-12-05"), nights: 4,  total_price: 11600,  status: "confirmed", created_at: new Date("2025-10-01") },
]);

// ------------------------------------------------------------
// Indexes
// ------------------------------------------------------------
db.users.createIndex({ login: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ first_name: "text", last_name: "text" });

db.hotels.createIndex({ city: 1 });
db.hotels.createIndex({ stars: 1 });

db.bookings.createIndex({ user_id: 1 });
db.bookings.createIndex({ hotel_id: 1 });
db.bookings.createIndex({ user_id: 1, status: 1 });
db.bookings.createIndex({ check_in: 1 });

print("✓ Data loaded: " +
  db.users.countDocuments()    + " users, " +
  db.hotels.countDocuments()   + " hotels, " +
  db.bookings.countDocuments() + " bookings");
