package com.scaleplane;

import com.scaleplane.generated.CompletionNotImplementedResponse;
import com.scaleplane.generated.CompletionRequest;
import com.scaleplane.generated.PromptResolveResponse;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ScalePlaneClientTest {
  private static final String PROMPT_ID = "11111111-1111-1111-1111-111111111111";
  private static final String PROJECT_ID = "22222222-2222-2222-2222-222222222222";
  private static final String VERSION_ID = "33333333-3333-3333-3333-333333333333";

  private MockWebServer server;
  private ScalePlaneClient client;

  @BeforeEach
  void setUp() throws IOException {
    server = new MockWebServer();
    server.start();
    client = new ScalePlaneClient(server.url("/api/v1").toString().replaceAll("/$", ""), "test-token");
  }

  @AfterEach
  void tearDown() throws IOException {
    server.shutdown();
  }

  @Test
  void resolvePrompt() throws Exception {
    server.enqueue(
        new MockResponse()
            .setResponseCode(200)
            .setHeader("Content-Type", "application/json")
            .setBody(
                """
                {
                  "prompt_id": "%s",
                  "prompt_slug": "system",
                  "tag": "production",
                  "version_id": "%s",
                  "version_number": 2,
                  "content": "You are helpful.",
                  "content_hash": "abc",
                  "metadata": null
                }
                """
                    .formatted(PROMPT_ID, VERSION_ID)));

    PromptResolveResponse result = client.prompts().resolve(PROMPT_ID);
    assertEquals("system", result.getPromptSlug());
    assertEquals(2, result.getVersionNumber());
    assertEquals("You are helpful.", result.getContent());

    RecordedRequest req = server.takeRequest(1, TimeUnit.SECONDS);
    assertTrue(req.getPath().contains("/prompts/" + PROMPT_ID + "/resolve"));
    assertEquals("Bearer test-token", req.getHeader("Authorization"));
  }

  @Test
  void resolveBySlug() throws Exception {
    server.enqueue(
        new MockResponse()
            .setHeader("Content-Type", "application/json")
            .setBody(
                """
                [{
                  "id": "%s",
                  "organization_id": "00000000-0000-0000-0000-000000000000",
                  "name": "Demo",
                  "slug": "demo",
                  "description": null,
                  "created_at": "2026-01-01T00:00:00Z"
                }]
                """
                    .formatted(PROJECT_ID)));
    server.enqueue(
        new MockResponse()
            .setHeader("Content-Type", "application/json")
            .setBody(
                """
                [{
                  "id": "%s",
                  "project_id": "%s",
                  "organization_id": "00000000-0000-0000-0000-000000000000",
                  "name": "System",
                  "slug": "system-prompt",
                  "description": null,
                  "created_at": "2026-01-01T00:00:00Z",
                  "latest_version_number": 1,
                  "production_tag_version": 1,
                  "environment_tags": {"production": 1, "staging": null, "dev": null}
                }]
                """
                    .formatted(PROMPT_ID, PROJECT_ID)));
    server.enqueue(
        new MockResponse()
            .setHeader("Content-Type", "application/json")
            .setBody(
                """
                {
                  "prompt_id": "%s",
                  "prompt_slug": "system-prompt",
                  "tag": "staging",
                  "version_id": "%s",
                  "version_number": 1,
                  "content": "hi",
                  "content_hash": "x",
                  "metadata": null
                }
                """
                    .formatted(PROMPT_ID, VERSION_ID)));

    PromptResolveResponse result = client.prompts().resolveBySlug("demo", "system-prompt", "staging");
    assertEquals("hi", result.getContent());
    assertEquals(3, server.getRequestCount());
  }

  @Test
  void missingProject() {
    server.enqueue(
        new MockResponse().setHeader("Content-Type", "application/json").setBody("[]"));
    assertThrows(NotFoundError.class, () -> client.prompts().resolveBySlug("missing", "system", "production"));
  }

  @Test
  void apiError() {
    server.enqueue(
        new MockResponse()
            .setResponseCode(404)
            .setHeader("Content-Type", "application/json")
            .setBody("{\"detail\":\"Tag not found\"}"));
    ApiError error = assertThrows(ApiError.class, () -> client.prompts().resolve(PROMPT_ID));
    assertEquals(404, error.status());
    assertEquals("Tag not found", error.detail());
  }

  @Test
  void completionsAccepts501() {
    server.enqueue(
        new MockResponse()
            .setResponseCode(501)
            .setHeader("Content-Type", "application/json")
            .setBody(
                """
                {
                  "detail": "SLM routing is not enabled in the MVP",
                  "message": "future",
                  "future_capabilities": ["Dynamic SLM / frontier model routing"]
                }
                """));
    CompletionRequest request =
        new CompletionRequest().promptSlug("system").tag("production").messages(List.of());
    CompletionNotImplementedResponse result = client.routing().completions(request);
    assertTrue(result.getDetail().contains("not enabled"));
  }

  @Test
  void requiresAuth() {
    assertThrows(
        IllegalArgumentException.class,
        () -> new ScalePlaneClient("http://example.test/api/v1", null, java.time.Duration.ofSeconds(5)));
  }
}
