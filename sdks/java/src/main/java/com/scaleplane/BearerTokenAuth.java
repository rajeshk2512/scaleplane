package com.scaleplane;

import java.util.Map;
import java.util.Objects;

public final class BearerTokenAuth implements AuthProvider {
  private final String token;

  public BearerTokenAuth(String token) {
    this.token = Objects.requireNonNull(token, "token");
  }

  @Override
  public Map<String, String> headers() {
    return Map.of("Authorization", "Bearer " + token);
  }
}
