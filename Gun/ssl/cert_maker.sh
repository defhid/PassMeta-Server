# root certificate
mkdir -p root

openssl genrsa -out root/CA.key 2048

openssl req -x509 -new -nodes -key root/CA.key -sha256 -days 3650 -out root/CA.pem -config config/domain.conf


# domain certificate
mkdir -p domain

openssl req -newkey rsa:2048 -sha256 -nodes -keyout domain/domain.key -out domain/domain.csr -config config/domain.conf

openssl x509 -req -in domain/domain.csr -CA root/CA.pem -CAkey root/CA.key -CAcreateserial -out domain/domain.crt -days 397 -sha256 -extfile config/domain.ext