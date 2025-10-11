let cachedEnv = null;

const requiredString = (value, key) => {
  if (!value || value.trim() === '') {
    throw new Error(`${key} is required`);
  }
  return value;
};

export const loadEnv = () => {
  if (cachedEnv) {
    return cachedEnv;
  }

  const errors = [];
  const { PORT, OPENAI_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY } = process.env;

  let port = 3000;
  if (PORT && Number.isFinite(Number(PORT))) {
    port = Number(PORT);
  } else if (PORT) {
    errors.push('PORT must be a number');
  }

  try {
    requiredString(OPENAI_API_KEY, 'OPENAI_API_KEY');
  } catch (error) {
    errors.push(error.message);
  }

  try {
    const value = requiredString(SUPABASE_URL, 'SUPABASE_URL');
    try {
      new URL(value);
    } catch {
      errors.push('SUPABASE_URL must be a valid URL');
    }
  } catch (error) {
    errors.push(error.message);
  }

  try {
    requiredString(SUPABASE_ANON_KEY, 'SUPABASE_ANON_KEY');
  } catch (error) {
    errors.push(error.message);
  }

  if (errors.length > 0) {
    throw new Error(`Environment validation failed: ${errors.join(', ')}`);
  }

  cachedEnv = {
    PORT: port,
    OPENAI_API_KEY: OPENAI_API_KEY.trim(),
    SUPABASE_URL: SUPABASE_URL.trim().replace(/\/$/, ''),
    SUPABASE_ANON_KEY: SUPABASE_ANON_KEY.trim()
  };

  return cachedEnv;
};
