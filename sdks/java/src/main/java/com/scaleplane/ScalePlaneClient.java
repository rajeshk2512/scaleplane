package com.scaleplane;

import com.scaleplane.resources.PromptsResource;
import com.scaleplane.resources.RoutingResource;

import java.time.Duration;

/** Facade: closed core + open resource mounts. */
public final class ScalePlaneClient {
  private final PromptsResource prompts;
  private final RoutingResource routing;

  public ScalePlaneClient(String baseUrl, String token) {
    this(baseUrl, new BearerTokenAuth(token), Duration.ofSeconds(30));
  }

  public ScalePlaneClient(String baseUrl, AuthProvider auth, Duration timeout) {
    if (auth == null) {
      throw new IllegalArgumentException("Provide token or auth");
    }
    ClientConfig config =
        new ClientConfig(
            baseUrl == null ? "http://127.0.0.1:8000/api/v1" : baseUrl, timeout);
    HttpTransport transport = new HttpTransport(config, auth);
    this.prompts = new PromptsResource(transport);
    this.routing = new RoutingResource(transport);
  }

  public PromptsResource prompts() {
    return prompts;
  }

  public RoutingResource routing() {
    return routing;
  }
}
