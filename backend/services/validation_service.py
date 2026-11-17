import hashlib
from typing import BinaryIO, Dict, Any, Tuple

VALID_DNA_CHARS = set(b"ACGTNacgtn\r\n ")
VALID_RNA_CHARS = set(b"ACGUNacgun\r\n ")
VALID_PROTEIN_CHARS = set(b"ACDEFGHIKLMNPQRSTVWYBZX*\r\n ")

class SequenceValidationService:
    CHUNK_SIZE = 65536  # 64 KB streaming buffer

    @staticmethod
    def validate_stream(
        stream: BinaryIO,
        format_type: str = "fasta",
        sequence_type: str = "dna"
    ) -> Dict[str, Any]:
        """
        Validates FASTA or FASTQ biological stream in O(1) memory.
        Calculates cryptographic SHA-256 digest on the fly.
        """
        hasher = hashlib.sha256()
        format_type = format_type.lower()
        sequence_type = sequence_type.lower()

        if sequence_type == "rna":
            valid_chars = VALID_RNA_CHARS
        elif sequence_type == "protein":
            valid_chars = VALID_PROTEIN_CHARS
        else:
            valid_chars = VALID_DNA_CHARS

        sequence_count = 0
        total_bp = 0
        errors = []
        is_valid = True

        buffer = bytearray()
        line_number = 0

        # FASTQ state machine: 0: header(@), 1: seq, 2: sep(+), 3: qual
        fastq_state = 0
        current_seq_len = 0
        current_qual_len = 0

        while True:
            chunk = stream.read(SequenceValidationService.CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
            buffer.extend(chunk)

            while True:
                newline_pos = buffer.find(b"\n")
                if newline_pos == -1:
                    break
                line = bytes(buffer[:newline_pos]).rstrip(b"\r")
                buffer = buffer[newline_pos + 1:]
                line_number += 1

                if not line:
                    continue

                if format_type == "fasta":
                    if line.startswith(b">"):
                        sequence_count += 1
                        if len(line) < 2:
                            errors.append(f"Line {line_number}: Empty FASTA header identifier")
                    else:
                        if sequence_count == 0:
                            errors.append(f"Line {line_number}: Sequence data preceded header")
                            is_valid = False
                        # Validate sequence characters
                        for b in line:
                            if b not in valid_chars:
                                errors.append(f"Line {line_number}: Invalid character '{chr(b)}' for {sequence_type}")
                                is_valid = False
                                break
                        total_bp += len(line)

                elif format_type == "fastq":
                    if fastq_state == 0:
                        if not line.startswith(b"@"):
                            errors.append(f"Line {line_number}: Expected FASTQ header starting with '@'")
                            is_valid = False
                        sequence_count += 1
                        current_seq_len = 0
                        fastq_state = 1
                    elif fastq_state == 1:
                        # Sequence line
                        for b in line:
                            if b not in valid_chars:
                                errors.append(f"Line {line_number}: Invalid sequence char '{chr(b)}'")
                                is_valid = False
                                break
                        current_seq_len = len(line)
                        total_bp += current_seq_len
                        fastq_state = 2
                    elif fastq_state == 2:
                        if not line.startswith(b"+"):
                            errors.append(f"Line {line_number}: Expected '+' separator")
                            is_valid = False
                        fastq_state = 3
                    elif fastq_state == 3:
                        current_qual_len = len(line)
                        if current_qual_len != current_seq_len:
                            errors.append(f"Line {line_number}: Quality length ({current_qual_len}) != Sequence length ({current_seq_len})")
                            is_valid = False
                        fastq_state = 0

        # Handle remaining buffer line
        if buffer:
            line = bytes(buffer).rstrip(b"\r")
            if line:
                line_number += 1
                if format_type == "fasta":
                    if line.startswith(b">"):
                        sequence_count += 1
                    else:
                        total_bp += len(line)
                elif format_type == "fastq" and fastq_state != 0:
                    errors.append(f"Line {line_number}: Incomplete FASTQ record at end of file")
                    is_valid = False

        if sequence_count == 0:
            errors.append("Empty biological sequence file (0 sequences parsed).")
            is_valid = False

        if errors:
            is_valid = False

        return {
            "is_valid": is_valid,
            "sha256": hasher.hexdigest(),
            "sequence_count": sequence_count,
            "total_bp": total_bp,
            "format": format_type,
            "sequence_type": sequence_type,
            "errors": errors[:20]  # Cap error list to prevent bloat
        }
