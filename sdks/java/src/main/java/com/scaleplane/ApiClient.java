package com.scaleplane;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Collection;
import java.util.Iterator;

/**
 * Minimal helpers required by OpenAPI Generator model {@code toUrlQueryString} methods.
 * Not part of the public ScalePlane SDK surface — do not use directly.
 */
public final class ApiClient {
  private ApiClient() {}

  public static String urlEncode(String s) {
    return URLEncoder.encode(s, StandardCharsets.UTF_8).replace("+", "%20");
  }

  public static String valueToString(Object value) {
    if (value == null) {
      return "";
    }
    if (value instanceof Collection<?> collection) {
      StringBuilder sb = new StringBuilder();
      Iterator<?> it = collection.iterator();
      if (it.hasNext()) {
        sb.append(valueToString(it.next()));
      }
      while (it.hasNext()) {
        sb.append(',').append(valueToString(it.next()));
      }
      return sb.toString();
    }
    return String.valueOf(value);
  }
}
