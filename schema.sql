CREATE TABLE IF NOT EXISTS attempts(
    id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    topic   TEXT NOT NULL,
    question   TEXT NOT NULL,
    user_answer   TEXT NOT NULL,
    score  SMALLINT NOT NULL CHECK (score BETWEEN 0 AND 5),
    grader_comment   TEXT,
    key_points   JSONB NOT NULL,
    covered_points   JSONB,
    missed_points   JSONB
);
