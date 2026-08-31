import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AryaCrypt } from "../src/AryaCrypt.js";
import { AryaCryptError, FormatError } from "../src/errors.js";
import * as format from "../src/format.js";
import { transformPassword } from "../src/preprocess.js";

describe("security validations", () => {
  it("counts non-BMP passwords by code point (emoji)", () => {
    const eightEmoji = "😀".repeat(8);
    assert.equal([...eightEmoji].length, 8);
    assert.equal(eightEmoji.length, 16); // UTF-16 code units
    const result = transformPassword(eightEmoji);
    assert.ok(result.stream.length > 0);
  });

  it("rejects short non-BMP passwords that look long in UTF-16", () => {
    const fourEmoji = "😀".repeat(4); // length 8 in UTF-16, 4 code points
    assert.equal(fourEmoji.length, 8);
    assert.throws(() => transformPassword(fourEmoji), AryaCryptError);
  });

  it("rejects invalid base64 metadata fields", () => {
    assert.throws(
      () =>
        format.decodeB64Field(
          { salt: "@@@", nonce: "AQID", auth_tag: "AQID", version: 1 } as any,
          "salt"
        ),
      FormatError
    );
  });

  it("rejects wrong salt length on encrypt options", async () => {
    const c = new AryaCrypt();
    await assert.rejects(
      () => c.encrypt(Buffer.from("hi"), "password1", { salt: Buffer.alloc(8) }),
      /salt must be/
    );
  });
});
