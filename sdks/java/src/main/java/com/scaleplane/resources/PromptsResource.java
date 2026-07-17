package com.scaleplane.resources;

import com.fasterxml.jackson.core.type.TypeReference;
import com.scaleplane.HttpTransport;
import com.scaleplane.NotFoundError;
import com.scaleplane.generated.ProjectResponse;
import com.scaleplane.generated.PromptResolveResponse;
import com.scaleplane.generated.PromptResponse;
import com.scaleplane.generated.PromptTagResponse;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Runtime prompt resolve / promote. Open for new methods; do not change transport. */
public final class PromptsResource {
  private final HttpTransport transport;

  public PromptsResource(HttpTransport transport) {
    this.transport = transport;
  }

  public PromptResolveResponse resolve(String promptId) {
    return resolve(promptId, "production");
  }

  public PromptResolveResponse resolve(String promptId, String tag) {
    return transport.request(
        "GET",
        "/prompts/" + promptId + "/resolve",
        Map.of("tag", tag),
        null,
        PromptResolveResponse.class,
        Set.of());
  }

  public PromptTagResponse promote(String promptId, String tag, Integer versionNumber) {
    Map<String, String> params = new HashMap<>();
    if (versionNumber != null) {
      params.put("version_number", String.valueOf(versionNumber));
    }
    return transport.request(
        "PUT",
        "/prompts/" + promptId + "/tags/" + tag,
        params.isEmpty() ? null : params,
        null,
        PromptTagResponse.class,
        Set.of());
  }

  public PromptResolveResponse resolveBySlug(String project, String prompt, String tag) {
    String promptId = lookupPromptId(project, prompt);
    return resolve(promptId, tag);
  }

  public PromptTagResponse promoteBySlug(
      String project, String prompt, String tag, Integer versionNumber) {
    String promptId = lookupPromptId(project, prompt);
    return promote(promptId, tag, versionNumber);
  }

  private String lookupPromptId(String project, String promptSlug) {
    UUID projectId = lookupProjectId(project);
    List<PromptResponse> prompts =
        transport.request(
            "GET",
            "/projects/" + projectId + "/prompts",
            null,
            null,
            new TypeReference<List<PromptResponse>>() {},
            Set.of());
    for (PromptResponse p : prompts) {
      if (promptSlug.equals(p.getSlug()) || promptSlug.equals(String.valueOf(p.getId()))) {
        return p.getId().toString();
      }
    }
    throw new NotFoundError("Prompt not found: " + promptSlug);
  }

  private UUID lookupProjectId(String project) {
    List<ProjectResponse> projects =
        transport.request(
            "GET",
            "/projects",
            null,
            null,
            new TypeReference<List<ProjectResponse>>() {},
            Set.of());
    for (ProjectResponse p : projects) {
      if (project.equals(p.getSlug()) || project.equals(String.valueOf(p.getId()))) {
        return p.getId();
      }
    }
    throw new NotFoundError("Project not found: " + project);
  }
}
