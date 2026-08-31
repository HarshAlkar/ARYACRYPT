export class AryaCryptError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AryaCryptError";
  }
}

export class AuthenticationError extends AryaCryptError {
  constructor(message: string) {
    super(message);
    this.name = "AuthenticationError";
  }
}

export class FormatError extends AryaCryptError {
  constructor(message: string) {
    super(message);
    this.name = "FormatError";
  }
}
