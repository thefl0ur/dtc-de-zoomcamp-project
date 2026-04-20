blob:
  server:
    port: "6124"

taskmanager:
  memory:
    process:
      size: 1728m
    jvm-metaspace:
      size: 512m
  bind-host: 0.0.0.0
  numberOfTaskSlots: 1

jobmanager:
  execution:
    failover-strategy: region
  rpc:
    address: jobmanager
    port: 6123
  memory:
    process:
      size: 800m
  bind-host: 0.0.0.0

query:
  server:
    port: "6125"

parallelism:
  default: 1

rest:
  address: 0.0.0.0

env:
  java:
    opts:
      all: >-
        --add-exports=java.rmi/sun.rmi.registry=ALL-UNNAMED
        --add-exports=java.security.jgss/sun.security.krb5=ALL-UNNAMED
        --add-opens=java.base/java.lang=ALL-UNNAMED
        --add-opens=java.base/java.net=ALL-UNNAMED
        --add-opens=java.base/java.io=ALL-UNNAMED
        --add-opens=java.base/java.nio=ALL-UNNAMED
        --add-opens=java.base/sun.nio.ch=ALL-UNNAMED
        --add-opens=java.base/java.lang.reflect=ALL-UNNAMED
        --add-opens=java.base/java.text=ALL-UNNAMED
        --add-opens=java.base/java.time=ALL-UNNAMED
        --add-opens=java.base/java.util=ALL-UNNAMED
        --add-opens=java.base/java.util.concurrent=ALL-UNNAMED
        --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED
        --add-opens=java.base/java.util.concurrent.locks=ALL-UNNAMED

s3.endpoint: "http://${minio_endpoint}"
s3.access-key: "${minio_user}"
s3.secret-key: "${minio_password}"
s3.path.style.access: "true"