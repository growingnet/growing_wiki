# Claim Extraction Benchmark

- paper_id: gradmax-2022
- model_id: nvidia/nemotron-3-super-120b-a12b:free
- status: failed
- error_kind: ValidationError
- error_message: 3 validation errors for WebsiteAlignedReviewerReport
claims.0
  Input should be a valid dictionary or instance of ClaimRecord [type=model_type, input_value='GradMax grows networks w...urbing learned behavior', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/model_type
claims.1
  Input should be a valid dictionary or instance of ClaimRecord [type=model_type, input_value='New weights are initiali...ximize useful gradients', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/model_type
claims.2
  Input should be a valid dictionary or instance of ClaimRecord [type=model_type, input_value='Improved training dynami...several vision settings', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/model_type
