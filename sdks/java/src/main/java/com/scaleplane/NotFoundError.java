package com.scaleplane;

public class NotFoundError extends ApiError {
  public NotFoundError(String detail) {
    super(404, detail);
  }
}
