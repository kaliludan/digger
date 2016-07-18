DROP TABLE IF EXISTS tracker_catalog, tracker_events;

-- User to tracking item mapping.
CREATE TABLE tracker_catalog(
  ID SERIAL PRIMARY KEY,
  USERNAME TEXT NOT NULL,
  APP VARCHAR(20) NOT NULL,
  NAME TEXT NOT NULL,
  UNIT VARCHAR(20),  -- Optional unit for the numeric value.
  LATEST_EVENT INTEGER,  -- Optional ID referencing latest event.
  CREATED_AT TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  DISABLED BOOLEAN DEFAULT FALSE  -- Soft deletion flag.
);

-- Expect frequent queries on (username, app).
CREATE INDEX tracker_catalog_user_idx ON tracker_catalog (USERNAME, APP);

-- Tracking item to event (when marked) mapping.
CREATE TABLE tracker_events(
  ID SERIAL PRIMARY KEY ,
  CATALOG_ID INTEGER REFERENCES tracker_catalog (ID),
  VALUE FLOAT4,  -- Optional numerical value. Absence means boolean is enough.
  MARKED_AT TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Expect queries fetching all event for a specific catalog (for example,
-- visualization / summary may need this).
CREATE INDEX tracker_events_catalog_idx ON tracker_events (CATALOG_ID);

-- Insert example data.
INSERT INTO tracker_catalog (USERNAME, APP, NAME, UNIT, LATEST_EVENT) VALUES (
  'edfward', 'console', 'building bot', 'hr', 2  -- Or change to 1.
);
INSERT INTO tracker_events (CATALOG_ID, VALUE, MARKED_AT) VALUES (
  1, 12, TIMESTAMP '2003-12-02 16:40:57'
);
INSERT INTO tracker_events (CATALOG_ID, VALUE) VALUES (
  1, 10
);
