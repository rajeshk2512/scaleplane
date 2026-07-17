package com.scaleplane;

import java.time.Duration;
import java.util.Objects;

public final class ClientConfig {
  private final String baseUrl;
  private final Duration timeout;

  public ClientConfig(String baseUrl, Duration timeout) {
    this.baseUrl = stripTrailingSlash(Objects.requireNonNull(baseUrl, "baseUrl"));
    this.timeout = Objects.requireNonNull(timeout, "timeout");
  }

  public String baseUrl() {
    return baseUrl;
  }

  public Duration timeout() {
    return timeout;
  }

  private static String stripTrailingSlash(String value) {
    return value.replaceAll("/+$", "");
  }
}
