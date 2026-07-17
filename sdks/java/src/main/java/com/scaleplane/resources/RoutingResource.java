package com.scaleplane.resources;

import com.scaleplane.HttpTransport;
import com.scaleplane.generated.CompletionNotImplementedResponse;
import com.scaleplane.generated.CompletionRequest;

import java.util.List;
import java.util.Set;

/** Routing / completions. Open for new methods; do not change transport. */
public final class RoutingResource {
  private final HttpTransport transport;

  public RoutingResource(HttpTransport transport) {
    this.transport = transport;
  }

  public CompletionNotImplementedResponse completions(CompletionRequest request) {
    CompletionRequest body = request;
    if (body == null) {
      body = new CompletionRequest().tag("production").messages(List.of());
    }
    return transport.request(
        "POST",
        "/route/completions",
        null,
        body,
        CompletionNotImplementedResponse.class,
        Set.of(501));
  }
}
