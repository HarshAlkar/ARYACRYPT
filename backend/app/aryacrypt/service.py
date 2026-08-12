"""
Purpose:
Acts as the central facade for the AryaCrypt Preprocessing Framework.

Documentation:
This service orchestrates the entire mathematical pipeline:
1. Validates the numeric seed.
2. Encodes the seed into base-100 chunks.
3. Translates chunks using the Roman Sanskrit Mapper.
4. Assembles fragments into a stream.
5. Validates the final stream's entropy.

It enforces Clean Architecture by wiring the concrete implementations
to the abstract interfaces internally.

Unit Test Suggestions:
- Pass a valid seed and ensure a phonetic string is returned.
- Pass an invalid seed and ensure ValueError is raised.
- Mock the entropy layer to fail and ensure it throws an error.
"""

from app.aryacrypt.validation import ValidationLayer
from app.aryacrypt.entropy_layer import EntropyLayer
from app.aryacrypt.positional_encoder import PositionalEncoder
from app.aryacrypt.roman_mapper import RomanSanskritMapper
from app.aryacrypt.encoding_engine import AryabhataEncodingEngine
from app.aryacrypt.stream_generator import NumericStreamGenerator

class AryaCryptService:
    
    def __init__(self):
        # Wiring dependencies
        self.encoder = PositionalEncoder()
        self.mapper = RomanSanskritMapper()
        self.engine = AryabhataEncodingEngine(self.encoder, self.mapper)
        self.stream_generator = NumericStreamGenerator()
        
    def generate_preprocessing_stream(self, numeric_seed: int) -> str:
        """
        Executes the entire AryaCrypt preprocessing framework pipeline.
        
        Args:
            numeric_seed (int): The raw numeric seed from the user.
            
        Returns:
            str: The high-entropy phonetic Aryabhata string ready for key derivation.
            
        Raises:
            ValueError: If the seed is invalid or the generated entropy is too low.
        """
        # Step 1: Validation
        ValidationLayer.validate_seed(numeric_seed)
        
        # Step 2 & 3: Encoding and Mapping
        fragments = self.engine.generate_phonetic_fragments(numeric_seed)
        
        # Step 4: Stream Generation
        final_stream = self.stream_generator.assemble_stream(fragments)
        
        # Step 5: Entropy Validation
        if not EntropyLayer.validate_minimum_entropy(final_stream, min_threshold=1.5):
            # If the seed is too small (e.g. 1 -> "ka"), entropy is low.
            # In a real-world scenario, we might salt it or reject it.
            # We'll reject it here to ensure robust security.
            raise ValueError(f"Generated stream '{final_stream}' lacks sufficient mathematical entropy for secure key derivation.")
            
        return final_stream
