# Claim Extraction Benchmark

- paper_id: growing-tiny-networks-2024
- model_id: nvidia/nemotron-3-super-120b-a12b:free
- status: failed
- error_type: ValidationError
- error_message: 4 validation errors for WebsiteAlignedReviewerReport
findings.0
  Input should be a valid dictionary or instance of ReviewFinding [type=model_type, input_value='CIFAR‑10/100 results m... manual design choices.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/model_type
claims.0
  Input should be a valid dictionary or instance of ClaimRecord [type=model_type, input_value='Expressivity bottlenecks...al gradient mismatches.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/model_type
claims.1
  Input should be a valid dictionary or instance of ClaimRecord [type=model_type, input_value="Adding neurons at detect...he functional gradient.", input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/model_type
claims.2
  Input should be a valid dictionary or instance of ClaimRecord [type=model_type, input_value='The resulting grown tiny...‑tuned architectures.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/model_type
