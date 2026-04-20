variable "minio_endpoint" { default = "minio:9000" }
variable "minio_user"     { default = "minioadmin" }
variable "minio_password" { default = "minioadmin" }
variable "broker" { default = "redpanda:29092" }
variable "broker_external" { default = "localhost:9092" }
variable "backend" { default = "s3" }