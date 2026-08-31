import {
  AVARGA_CONSONANTS,
  AVARGA_START_TENS,
  VARGA_CONSONANTS,
  VOWEL_MULTIPLIERS,
} from "./constants.js";

export class AryabhataMapping {
  private vargaValToSym = new Map<number, string>();
  private avargaValToSym = new Map<number, string>();
  private vowelValToSym = new Map<number, string>();
  readonly vowelCount: number;

  constructor() {
    VARGA_CONSONANTS.forEach((symbol, index) => {
      this.vargaValToSym.set(index + 1, symbol);
    });
    let tens = AVARGA_START_TENS;
    for (const symbol of AVARGA_CONSONANTS) {
      this.avargaValToSym.set(tens, symbol);
      tens += 10;
    }
    VOWEL_MULTIPLIERS.forEach((symbol, power) => {
      this.vowelValToSym.set(power, symbol);
    });
    this.vowelCount = VOWEL_MULTIPLIERS.length;
  }

  getVargaSymbol(value: number): string | undefined {
    return this.vargaValToSym.get(value);
  }

  getAvargaSymbol(value: number): string | undefined {
    return this.avargaValToSym.get(value);
  }

  getVowelSymbol(power: number): string | undefined {
    return this.vowelValToSym.get(power);
  }
}
