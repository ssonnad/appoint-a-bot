# Curl Examples for the Booking API

This document provides curl examples for interacting with the Booking API.

## Health Check

Check if the API is running:

```bash
curl -X GET "http://localhost:8080/health"
```

## Get Available Slots

Retrieve available appointment slots:

```bash
# Get all available slots for the next 7 days
curl -X GET "http://localhost:8080/api/slots"

# Get slots with specific date range
curl -X GET "http://localhost:8080/api/slots?start_date=2025-06-01T00:00:00&end_date=2025-06-07T23:59:59"

# Get slots with transport options
curl -X GET "http://localhost:8080/api/slots?include_transport=true"

# Get slots at a specific location
curl -X GET "http://localhost:8080/api/slots?location_id=loc1"
```

## Create a Manual Booking

Create a booking for a specific time slot:

```bash
curl -X POST "http://localhost:8080/api/bookings" \
  -H "Content-Type: application/json" \
  -d '{
    "slot_id": "slot-202506021000-loc1",
    "customer_info": {
      "vehicle_id": "VIN12345",
      "customer_id": "CUST123",
      "vehicle_make": "Toyota",
      "vehicle_model": "Camry",
      "vehicle_year": 2020,
      "mileage": 35000
    }
  }'
```

## Create a DTC-Triggered Booking

Process a DTC code and create a booking:

```bash
curl -X POST "http://localhost:8080/api/dtc-booking" \
  -H "Content-Type: application/json" \
  -d '{
    "dtc_code": "C0045",
    "vehicle_id": "VIN13579",
    "timestamp": "2025-06-01T12:00:00Z",
    "additional_info": {
      "mileage": 45000,
      "customer_id": "CUST321",
      "vehicle_make": "BMW",
      "vehicle_model": "X5",
      "vehicle_year": 2022,
      "brake_pad_thickness": "2mm"
    }
  }'
```

## Get Booking Information

Retrieve booking information:

```bash
# Get all bookings
curl -X GET "http://localhost:8080/api/bookings"

# Get a specific booking by ID
curl -X GET "http://localhost:8080/api/bookings/BOOK-12345678"
```

## Usage Flow

1. Start the booking API:
   ```bash
   python -m src.appoint_a_bot.main booking-api
   ```

2. Get available slots to find a slot ID:
   ```bash
   curl -X GET "http://localhost:8080/api/slots"
   ```

3. Create a booking using a slot ID:
   ```bash
   curl -X POST "http://localhost:8080/api/bookings" -H "Content-Type: application/json" -d '{"slot_id": "SLOT_ID_HERE", "customer_info": {"vehicle_id": "VIN12345", "customer_id": "CUST123"}}'
   ```

4. Alternatively, create a booking triggered by a DTC code:
   ```bash
   curl -X POST "http://localhost:8080/api/dtc-booking" -H "Content-Type: application/json" -d '{"dtc_code": "C0045", "vehicle_id": "VIN13579"}'
   ```

5. View all bookings:
   ```bash
   curl -X GET "http://localhost:8080/api/bookings"
   ``` 