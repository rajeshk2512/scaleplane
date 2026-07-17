package com.scaleplane;

import java.util.Map;

/** Extension point for auth strategies (Bearer today; API keys later). */
public interface AuthProvider {
  Map<String, String> headers();
}
