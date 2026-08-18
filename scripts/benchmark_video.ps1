param(
  [string]$Model = "Wan-AI/Wan2.2-TI2V-5B",
  [string]$Output = "./benchmark_output/video.mp4",
  [int]$Width = 512,
  [int]$Height = 512,
  [int]$Frames = 40,
  [int]$Fps = 8
)

$ErrorActionPreference = "Stop"

python -m app.services.real_benchmark.cli `
  --model $Model `
  --output $Output `
  --width $Width `
  --height $Height `
  --frames $Frames `
  --fps $Fps
