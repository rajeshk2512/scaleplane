package com.scaleplane;

public class ApiError extends RuntimeException {
  private final int status;
  private final String detail;

  public ApiError(int status, String detail) {
    super(status + ": " + detail);
    this.status = status;
    this.detail = detail;
  }

  public int status() {
    return status;
  }

  public String detail() {
    return detail;
  }
}
