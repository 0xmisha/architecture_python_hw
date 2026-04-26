// ============================================================
// Hotel Booking System — JSON Schema Validation (Variant 13)
// Run in mongosh: load("validation.js")
// ============================================================

use("hotel_booking");

// ------------------------------------------------------------
// Helper: drop & recreate collection with validator
// ------------------------------------------------------------
function createValidatedCollection(name, validator) {
  try { db[name].drop(); } catch(e) {}
  db.createCollection(name, {
    validator:        { $jsonSchema: validator },
    validationLevel:  "strict",
    validationAction: "error"
  });
  print("✓ Created collection '" + name + "' with $jsonSchema validation");
}

// ============================================================
// users
// ============================================================
createValidatedCollection("users", {
  bsonType: "object",
  required: ["login", "password_hash", "first_name", "last_name", "email", "created_at"],
  additionalProperties: false,
  properties: {
    _id:           { bsonType: "objectId" },
    login: {
      bsonType:    "string",
      minLength:   3,
      maxLength:   50,
      description: "Unique login, 3-50 chars"
    },
    password_hash: { bsonType: "string", minLength: 1 },
    first_name:    { bsonType: "string", minLength: 1, maxLength: 100 },
    last_name:     { bsonType: "string", minLength: 1, maxLength: 100 },
    email: {
      bsonType:    "string",
      pattern:     "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$",
      description: "Valid email address"
    },
    created_at:    { bsonType: "date" }
  }
});

// ============================================================
// hotels
// ============================================================
createValidatedCollection("hotels", {
  bsonType: "object",
  required: ["name", "city", "address", "stars", "rooms_total", "price_per_night", "created_at"],
  properties: {
    _id:             { bsonType: "objectId" },
    name:            { bsonType: "string", minLength: 1, maxLength: 255 },
    city:            { bsonType: "string", minLength: 1, maxLength: 100 },
    address:         { bsonType: "string", minLength: 1, maxLength: 500 },
    stars: {
      bsonType:    "int",
      minimum:     1,
      maximum:     5,
      description: "Star rating 1–5"
    },
    rooms_total: {
      bsonType:    "int",
      minimum:     1,
      description: "Must be positive"
    },
    price_per_night: {
      bsonType:    "double",
      minimum:     0.01,
      description: "Price must be > 0"
    },
    amenities: {
      bsonType: "array",
      items:    { bsonType: "string" }
    },
    created_at: { bsonType: "date" }
  }
});

// ============================================================
// bookings
// ============================================================
createValidatedCollection("bookings", {
  bsonType: "object",
  required: ["user_id", "hotel_id", "hotel_snapshot", "check_in", "check_out", "nights", "total_price", "status", "created_at"],
  properties: {
    _id:      { bsonType: "objectId" },
    user_id:  { bsonType: "objectId" },
    hotel_id: { bsonType: "objectId" },
    hotel_snapshot: {
      bsonType: "object",
      required: ["name", "city", "price_per_night"],
      properties: {
        name:            { bsonType: "string" },
        city:            { bsonType: "string" },
        price_per_night: { bsonType: "double" }
      }
    },
    check_in:  { bsonType: "date" },
    check_out: { bsonType: "date" },
    nights: {
      bsonType: "int",
      minimum:  1,
      description: "At least 1 night"
    },
    total_price: {
      bsonType: "double",
      minimum:  0,
      description: "Non-negative total price"
    },
    status: {
      bsonType: "string",
      enum:     ["confirmed", "cancelled"],
      description: "confirmed or cancelled"
    },
    created_at: { bsonType: "date" }
  }
});

// ============================================================
// Test valid insert
// ============================================================
print("\n--- Testing valid insert (users) ---");
try {
  db.users.insertOne({
    login:         "valid_user",
    password_hash: "$2b$12$...",
    first_name:    "Валидный",
    last_name:     "Пользователь",
    email:         "valid@example.com",
    created_at:    new Date()
  });
  print("✓ Valid user inserted successfully");
} catch(e) {
  print("✗ Unexpected error: " + e.message);
}

// ============================================================
// Test invalid inserts (must fail)
// ============================================================
print("\n--- Testing invalid inserts (expect errors) ---");

// Missing required field
try {
  db.users.insertOne({ login: "no_email", password_hash: "x", first_name: "A", last_name: "B", created_at: new Date() });
  print("✗ Should have failed (missing email)");
} catch(e) {
  print("✓ Rejected (missing email): " + e.message.substring(0, 80));
}

// Invalid email format
try {
  db.users.insertOne({ login: "bad_email", password_hash: "x", first_name: "A", last_name: "B", email: "not-an-email", created_at: new Date() });
  print("✗ Should have failed (bad email)");
} catch(e) {
  print("✓ Rejected (bad email format): " + e.message.substring(0, 80));
}

// Login too short
try {
  db.users.insertOne({ login: "ab", password_hash: "x", first_name: "A", last_name: "B", email: "x@y.com", created_at: new Date() });
  print("✗ Should have failed (login < 3 chars)");
} catch(e) {
  print("✓ Rejected (login too short): " + e.message.substring(0, 80));
}

// Hotel: stars out of range
try {
  db.hotels.insertOne({ name: "Bad Hotel", city: "Moscow", address: "Addr", stars: 6, rooms_total: 10, price_per_night: 1000.0, created_at: new Date() });
  print("✗ Should have failed (stars = 6)");
} catch(e) {
  print("✓ Rejected (stars > 5): " + e.message.substring(0, 80));
}

// Hotel: negative price
try {
  db.hotels.insertOne({ name: "Bad Hotel", city: "Moscow", address: "Addr", stars: 3, rooms_total: 10, price_per_night: -100.0, created_at: new Date() });
  print("✗ Should have failed (negative price)");
} catch(e) {
  print("✓ Rejected (negative price): " + e.message.substring(0, 80));
}

// Booking: invalid status
try {
  db.bookings.insertOne({
    user_id:  ObjectId(), hotel_id: ObjectId(),
    hotel_snapshot: { name: "X", city: "Y", price_per_night: 1000.0 },
    check_in: new Date(), check_out: new Date(), nights: 1, total_price: 1000.0,
    status: "pending",   // not in enum
    created_at: new Date()
  });
  print("✗ Should have failed (status=pending)");
} catch(e) {
  print("✓ Rejected (invalid status): " + e.message.substring(0, 80));
}

print("\n✓ Validation tests complete");
