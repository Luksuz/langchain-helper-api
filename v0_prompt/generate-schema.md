### /generate-schema — AI-powered database schema generation for v0 projects

Use this to automatically generate PostgreSQL database schemas based on your project description. Perfect for rapidly prototyping v0 applications that need custom database structures without manual SQL writing.

**Features:**
- AI-powered schema analysis using OpenAI GPT models
- Automatic table name UUID postfixing for app isolation
- Production-ready PostgreSQL schemas with indexes and relationships
- Sample data insertion for immediate testing
- Detailed explanations of generated structures

Sample request
```http
POST /generate-schema
Content-Type: application/json

{
  "project_description": "A weather tracking application that stores daily weather data including temperature, humidity, pressure, wind speed, and weather conditions for different cities",
  "additional_requirements": "Include historical data storage and ability to track multiple weather stations per city",
  "model": "gpt-4o-mini",
  "temperature": 0.1
}
```

Sample response
```json
{
  "success": true,
  "sql_schema": "CREATE TABLE cities_a1b2c3d4 (\n  id SERIAL PRIMARY KEY,\n  name VARCHAR(255) NOT NULL,\n  country VARCHAR(100) NOT NULL,\n  latitude DECIMAL(10,8),\n  longitude DECIMAL(11,8),\n  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);\n\nCREATE TABLE weather_data_a1b2c3d4 (\n  id SERIAL PRIMARY KEY,\n  city_id INTEGER REFERENCES cities_a1b2c3d4(id),\n  temperature DECIMAL(5,2),\n  humidity INTEGER,\n  pressure DECIMAL(7,2),\n  wind_speed DECIMAL(5,2),\n  conditions VARCHAR(100),\n  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);\n\nCREATE INDEX idx_weather_data_a1b2c3d4_city_date ON weather_data_a1b2c3d4(city_id, recorded_at);",
  "app_uuid": "a1b2c3d4",
  "tables_created": [
    "cities_a1b2c3d4",
    "weather_data_a1b2c3d4",
    "weather_stations_a1b2c3d4"
  ],
  "explanation": "Generated database schema for: A weather tracking application...\n\nApp UUID: a1b2c3d4\n\nCreated 3 tables:\n- cities_a1b2c3d4 (stores cities data)\n- weather_data_a1b2c3d4 (stores weather_data data)\n- weather_stations_a1b2c3d4 (stores weather_stations data)"
}
```

**Use Cases:**
- Rapid prototyping of v0 applications with custom data needs
- Generating schemas for e-commerce, blog, CRM, inventory systems
- Creating isolated database structures for different app instances  
- Learning proper database design patterns
- Bootstrapping new projects with production-ready schemas

**Parameters:**
- `project_description`: Description of your project and its data requirements
- `additional_requirements` (optional): Specific technical requirements or constraints
- `model` (optional): OpenAI model to use (default: "gpt-4o-mini")
- `temperature` (optional): Creativity level 0.0-1.0 (default: 0.1)

**Response Format:**
- `success`: Boolean indicating generation success
- `sql_schema`: Complete SQL schema ready for /setup-db
- `app_uuid`: Unique identifier used for table name postfixes  
- `tables_created`: Array of table names that will be created
- `explanation`: Human-readable description of the generated schema
- `message`: Error message if success is false

**Integration Workflow:**
1. Call `/generate-schema` with your project description
2. Review the generated SQL schema and table names
3. Use `/setup-db` with the returned `sql_schema` to create tables
4. Use `/query-db` with UUID-postfixed table names for data operations
5. Each app instance gets isolated tables thanks to unique UUID postfixes

**Environment Variables:**
- `OPENAI_API_KEY`: Required for AI-powered schema generation
