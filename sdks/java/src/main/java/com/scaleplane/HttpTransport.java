package com.scaleplane;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/** Closed HTTP layer — resources call this; do not extend per feature. */
public final class HttpTransport {
  private final ClientConfig config;
  private final AuthProvider auth;
  private final HttpClient httpClient;
  private final ObjectMapper mapper;

  public HttpTransport(ClientConfig config, AuthProvider auth) {
    this.config = config;
    this.auth = auth;
    this.httpClient = HttpClient.newBuilder().connectTimeout(config.timeout()).build();
    this.mapper = new ObjectMapper().registerModule(new JavaTimeModule());
  }

  public <T> T request(
      String method,
      String path,
      Map<String, String> params,
      Object body,
      Class<T> responseType,
      Set<Integer> acceptStatuses
  ) {
    return request(method, path, params, body, responseType, null, acceptStatuses);
  }

  public <T> T request(
      String method,
      String path,
      Map<String, String> params,
      Object body,
      TypeReference<T> typeReference,
      Set<Integer> acceptStatuses
  ) {
    return request(method, path, params, body, null, typeReference, acceptStatuses);
  }

  private <T> T request(
      String method,
      String path,
      Map<String, String> params,
      Object body,
      Class<T> responseType,
      TypeReference<T> typeReference,
      Set<Integer> acceptStatuses
  ) {
    try {
      String query = "";
      if (params != null && !params.isEmpty()) {
        query =
            params.entrySet().stream()
                .filter(e -> e.getValue() != null)
                .map(e -> encode(e.getKey()) + "=" + encode(e.getValue()))
                .collect(Collectors.joining("&", "?", ""));
      }
      URI uri = URI.create(config.baseUrl() + path + query);
      HttpRequest.Builder builder =
          HttpRequest.newBuilder(uri)
              .timeout(config.timeout())
              .header("Accept", "application/json")
              .header("Content-Type", "application/json");
      auth.headers().forEach(builder::header);

      if (body != null) {
        builder.method(method, HttpRequest.BodyPublishers.ofString(mapper.writeValueAsString(body)));
      } else {
        builder.method(method, HttpRequest.BodyPublishers.noBody());
      }

      HttpResponse<String> response =
          httpClient.send(builder.build(), HttpResponse.BodyHandlers.ofString());
      int status = response.statusCode();
      boolean ok = status < 400 || (acceptStatuses != null && acceptStatuses.contains(status));
      if (!ok) {
        throw new ApiError(status, extractDetail(response.body(), status));
      }
      if (status == 204 || response.body() == null || response.body().isBlank()) {
        return null;
      }
      if (typeReference != null) {
        return mapper.readValue(response.body(), typeReference);
      }
      return mapper.readValue(response.body(), responseType);
    } catch (ApiError e) {
      throw e;
    } catch (IOException | InterruptedException e) {
      if (e instanceof InterruptedException) {
        Thread.currentThread().interrupt();
      }
      throw new ApiError(0, e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage());
    }
  }

  private static String encode(String value) {
    return URLEncoder.encode(value, StandardCharsets.UTF_8);
  }

  private String extractDetail(String body, int status) {
    try {
      JsonNode node = mapper.readTree(body);
      JsonNode detail = node.get("detail");
      if (detail != null && !detail.isNull()) {
        return detail.isTextual() ? detail.asText() : detail.toString();
      }
    } catch (Exception ignored) {
      // fall through
    }
    return body == null || body.isBlank() ? "HTTP " + status : body;
  }
}
