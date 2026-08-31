import { AryaCrypt } from "../src/index.ts";

const crypto = new AryaCrypt();
const blob = await crypto.encrypt(Buffer.from("hello from example"), "example1");
const plain = await crypto.decrypt(blob, "example1");
console.log("ok", blob.length, "bytes", Buffer.from(plain).toString());
