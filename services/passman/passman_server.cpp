#include <iostream>
#include <fstream>
#include <cstdint>

#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <byteswap.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>


using namespace std;

const uint32_t SHA256_K[256] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

const int MAX_PASS_PER_LOGIN = 8;

static uint32_t rotr(uint32_t num, int count) {
    return num >> count | (num << (32 - count));
}

void print_hex(uint8_t* msg, int msglen) {
    for (int i = 0; i < msglen; i += 1) {
        printf("%02x", (uint8_t)msg[i]);
    }
    printf("\n");
}

static int div_like_in_python(int a, int b) {
    return ((a % b) + b) % b;
}

void sha256(const uint8_t* msg, int msglen, uint8_t *out) {
    uint32_t ss[8] = {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};

    uint8_t chunk[64];
    uint8_t padding[64] = {0x80, 0};

    int padding_len = 1 + div_like_in_python((64 - (msglen + 1 + 8) ), 64 ) + 8;

    *(uint64_t *)(&padding[padding_len - 8]) = __bswap_64(msglen*8);

    // printf("padding_len=%d last_chunk_num %d\n", padding_len, last_chunk_num);

    int padding_ptr = 0;
    for (int chunk_num = 0; chunk_num < (msglen+padding_len) / 64 ; chunk_num += 1) {
        int copied = chunk_num * 64;
        int left = msglen - copied;

        if (left >= 64) {
            memcpy(chunk, &msg[64*chunk_num], 64);
        } else {
            if(left < 0) {
                left = 0;
            }
            memcpy(chunk, &msg[64*chunk_num], left);
            int space_in_block = 64 - left;

            memcpy(chunk+left, padding+padding_ptr, 64 - left);
            padding_ptr += (64 - left);
        }

        uint32_t w[64];
        for (int i = 0; i < 16; i += 1) {
            w[i] = __bswap_32(*(uint32_t *)(&chunk[i*4]));
        }

        for (int i = 16; i < 64; i += 1) {
            uint32_t a = rotr(w[i-15], 7) ^ rotr(w[i-15], 18) ^ (w[i-15] >> 3);
            uint32_t b = rotr(w[i-2], 17) ^ rotr(w[i-2], 19) ^ (w[i-2] >> 10);
            w[i] = a + b + w[i-16] + w[i-7];

        }

        uint32_t s[8];
        for (int i = 0; i < 8; i+=1) {
            s[i] = ss[i];
        }

        for (int i = 0; i < 64; i+= 1) {
            uint32_t c = (s[4] & s[5]) ^ ((s[4] ^ 0xffffffff) & s[6]);
            uint32_t t = SHA256_K[i] + s[7] + c + w[i] +
                         (rotr(s[4], 6) ^ rotr(s[4], 11) ^ rotr(s[4], 25));
            uint32_t q = rotr(s[0], 2) ^ rotr(s[0], 13) ^ rotr(s[0], 22);
            uint32_t m = (s[0] & s[1]) ^ (s[0] & s[2]) ^ (s[1] & s[2]);

            s[7] = s[6];
            s[6] = s[5];
            s[5] = s[4];
            s[4] = s[3] + t;
            s[3] = s[2];
            s[2] = s[1];
            s[1] = s[0];
            s[0] = q + m + t;
        }

        for (int i = 0; i < 8; i += 1) {
            ss[i] += s[i];
        }
    }

    for (int i = 0; i < 8; i += 1) {
        *(uint32_t*)(&out[i*4]) = __bswap_32(ss[i]);
    }
}

const uint8_t SBOX[256] = {
    99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125,
    250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204,
    52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235,
    39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209,
    0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251, 67, 77, 51,
    133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33,
    16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96,
    129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36,
    92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244,
    234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139,
    138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17,
    105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104,
    65, 153, 45, 15, 176, 84, 187, 22
};

const int ROUNDS = 10;

void expand_key(uint8_t* key, uint32_t out_key[ROUNDS+1][4]) {
    const uint8_t RCON[10] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36};

    for (int i = 0; i < 4; i += 1) {
        out_key[0][i] = __bswap_32(*(uint32_t*)&key[i*4]);
    }

    for (int i = 1; i < ROUNDS+1; i += 1) {
        uint32_t *prev_key = out_key[i - 1];

        out_key[i][0] = ((SBOX[(prev_key[3] >> 8*2) & 0xFF] << 8*3) ^
                          (SBOX[(prev_key[3] >> 8*1) & 0xFF] << 8*2) ^
                          (SBOX[(prev_key[3] >> 8*0) & 0xFF] << 8*1) ^
                          (SBOX[(prev_key[3] >> 8*3) & 0xFF] << 8*0) ^
                          (RCON[i-1] << 8*3) ^ prev_key[0]);

        for (int j = 1; j < 4; j += 1) {
            out_key[i][j] = out_key[i][j-1] ^ prev_key[j];
        }
    }
}

void encrypt(uint8_t* key, uint8_t* block, uint8_t* out_block) {
    uint8_t two_times[256];
    for (int i = 0; i < 256; i += 1) {
        two_times[i] = 2*i < 256 ? 2*i : (2*i) ^ 27;
    }

    uint32_t enc_keys[ROUNDS+1][4];

    expand_key(key, enc_keys);

    uint32_t t[4];
    for (int i = 0; i < 4; i += 1) {
        t[i] = __bswap_32(*(uint32_t *)(&block[i*4])) ^ enc_keys[0][i];
    }

    for (int r = 1; r < ROUNDS; r += 1) {
        uint32_t old_t[4];
        for (int i = 0; i < 4; i += 1) {
            old_t[i] = t[i];
        }
        for (int i = 0; i < 4; i += 1) {
            t[i] = (SBOX[(old_t[(i + 0) % 4] >> 8*3) & 0xFF]) << 8*3 |
                   (SBOX[(old_t[(i + 1) % 4] >> 8*2) & 0xFF]) << 8*2 |
                   (SBOX[(old_t[(i + 2) % 4] >> 8*1) & 0xFF]) << 8*1 |
                   (SBOX[(old_t[(i + 3) % 4] >> 8*0) & 0xFF]) << 8*0;
        }

        for (int i = 0; i < 4; i += 1) {
            old_t[i] = t[i];
        }

        for (int i = 0; i < 4; i += 1) {
            uint8_t *c = (uint8_t*) &old_t[i];
            ((uint8_t*)&t[i])[0] = c[3] ^ c[2] ^ c[1] ^ two_times[c[0] ^ c[3]];
            ((uint8_t*)&t[i])[1] = c[3] ^ c[2] ^ c[0] ^ two_times[c[1] ^ c[0]];
            ((uint8_t*)&t[i])[2] = c[3] ^ c[1] ^ c[0] ^ two_times[c[2] ^ c[1]];
            ((uint8_t*)&t[i])[3] = c[2] ^ c[1] ^ c[0] ^ two_times[c[3] ^ c[2]];
        }

        for (int i = 0; i < 4; i += 1) {
            t[i] ^= enc_keys[r][i];
        }
    }

    for (int i = 0; i < 4; i += 1) {
        out_block[4*i+0] = SBOX[(t[(i + 0) % 4] >> 8*3) & 0xFF] ^ (enc_keys[ROUNDS][i] >> 8*3) & 0xFF;
        out_block[4*i+1] = SBOX[(t[(i + 1) % 4] >> 8*2) & 0xFF] ^ (enc_keys[ROUNDS][i] >> 8*2) & 0xFF;
        out_block[4*i+2] = SBOX[(t[(i + 2) % 4] >> 8*1) & 0xFF] ^ (enc_keys[ROUNDS][i] >> 8*1) & 0xFF;
        out_block[4*i+3] = SBOX[(t[(i + 3) % 4] >> 8*0) & 0xFF] ^ (enc_keys[ROUNDS][i] >> 8*0) & 0xFF;
    }
}

class RandomGen {
    uint8_t state[32];
public:
    __attribute__ ((noinline)) RandomGen() {
        ifstream fstr("/dev/urandom");
        if (!fstr.is_open()) {
            cerr<<"Err open\n";
            exit(1);
        }
        fstr.read(reinterpret_cast<char*>(state), 32);
    }

    __attribute__ ((noinline)) uint32_t get_random() {
        sha256(state, 32, state);
        return *(uint32_t*) state;
    }
};


int read_packet_or_die(int client_socket, uint8_t* buf) {
    uint8_t got_bytes = 0;

    uint8_t pkt_len;

    if (recv(client_socket, &pkt_len, 1, 0) != 1) {
        return 0;
    }

    while (got_bytes < pkt_len) {
        int got_this_time = recv(client_socket, &buf[got_bytes], pkt_len-got_bytes, 0);
        if (got_this_time <= 0) {
            exit(1);
        }
        got_bytes += got_this_time;
    }

    return pkt_len;
}

int write_packet_or_die(int client_socket, uint8_t* buf, uint8_t len) {
    uint8_t sent_bytes = 0;

    if (send(client_socket, &len, 1, 0) != 1) {
        return 0;
    }

    while (sent_bytes < len) {
        int sent_this_time = send(client_socket, &buf[sent_bytes], len-sent_bytes, 0);
        if (sent_this_time <= 0) {
            exit(1);
        }
        sent_bytes += sent_this_time;
    }
    return sent_bytes;
}


void hash_to_hex(uint8_t* hash, char *hex) {
    for(int i = 0; i < 32; i += 1) {
        sprintf(&hex[i*2], "%02x", hash[i]);
    }
    hex[64] = 0;
}

int write_login_pass(int fd, int offset,
                     uint8_t* login, uint8_t login_length,
                     uint8_t* password, uint8_t password_length) {
    uint8_t nulls[256] = {0};

    if (offset >= MAX_PASS_PER_LOGIN) {
        return 0;
    }

    if(lseek(fd, offset*(256*2), SEEK_SET) == -1) {
        return 0;
    }

    if (write(fd, &login_length, 1) != 1) {
        return 0;
    }
    if (write(fd, login, login_length) != login_length) {
        return 0;
    }
    if (write(fd, nulls, 255-login_length) != (255-login_length)) {
        return 0;
    }
    if (write(fd, &password_length, 1) != 1) {
        return 0;
    }
    if (write(fd, password, password_length) != password_length) {
        return 0;
    }
    if (write(fd, nulls, 255-password_length) != (255-password_length)) {
        return 0;
    }
    return 1;
}


int init_user(int fd_user_pass, int fd_users, uint8_t* login, uint8_t login_length,
              uint8_t* password, uint8_t password_length) {
    uint8_t nulls[256] = {0};

    if(lseek(fd_users, 0, SEEK_SET) == -1) {
        return 0;
    }

    if (write(fd_users, &login_length, 1) != 1) {
        return 0;
    }
    if (write(fd_users, login, login_length) != login_length) {
        return 0;
    }
    if (write(fd_users, nulls, 255-login_length) != (255-login_length)) {
        return 0;
    }

    if (lseek(fd_user_pass, 0, SEEK_SET) == -1) {
        return 0;
    }

    for (int i = 0; i < MAX_PASS_PER_LOGIN * 2; i += 1) {
        if (write(fd_user_pass, nulls, 256) != 256) {
            return 0;
        }
    }

    // zeroth pos is login password
    return write_login_pass(fd_user_pass, 0, login, login_length, password, password_length);
}


int send_user_with_num(int client_socket, uint32_t user_pos, int fd) {
    uint8_t user_buf[256+1] = {};

    int max_pos = lseek(fd, 0, SEEK_END);
    if (max_pos == -1) {
        return 0;
    }

    uint32_t users_count = max_pos / 256;

    if (user_pos >= users_count) {
        return 0;
    }

    uint32_t user_to_send = users_count - user_pos - 1;

    if (lseek(fd, user_to_send*256, SEEK_SET) == -1) {
        return 0;
    }

    if (read(fd, user_buf+1, 256) != 256) {
        return 0;
    }
    user_buf[0] = 0x1;

    return write_packet_or_die(client_socket, user_buf, user_buf[1] + 1 + 1) > 0;
}


int get_pass_by_offset(int fd, int offset,
                       uint8_t* password_name, uint8_t* password_name_length,
                       uint8_t* password, uint8_t* password_length) {
    char buf[512];

    if (offset >= MAX_PASS_PER_LOGIN) {
        return 0;
    }

    if (lseek(fd, offset*512, SEEK_SET) == -1) {
        return 0;
    }

    if (read(fd, buf, 512) != 512) {
        return 0;
    }

    *password_name_length = buf[0];
    memcpy(password_name, &buf[1], *password_name_length);

    *password_length = buf[256];
    memcpy(password, &buf[257], *password_length);

    return 1;
}

int set_pass_by_offset(int fd, int offset,
                       uint8_t* password_name, uint8_t password_name_length,
                       uint8_t* password, uint8_t password_length) {

    char buf[512] = {0};

    if (offset >= MAX_PASS_PER_LOGIN) {
        return 0;
    }

    if (lseek(fd, offset*512, SEEK_SET) == -1) {
        return 0;
    }

    buf[0] = password_name_length;
    memcpy(&buf[1], password_name, password_name_length);

    buf[256] = password_length;
    memcpy(&buf[257], password, password_length);

    if (write(fd, buf, 512) != 512) {
        return 0;
    }

    return 1;
}


int send_error_or_die(int client_socket) {
    uint8_t error_code = 0xff;
    return write_packet_or_die(client_socket, &error_code, 1) > 0;
}


int handle_client(int client_socket) {
    uint8_t login[256] = {};
    uint8_t login_length = 0;
    uint8_t password[256] = {};
    uint8_t password_length = 0;
    uint8_t password_name[256] = {};
    uint8_t password_name_length = 0;
    uint8_t login_hash[32];
    uint8_t out_buf[512] = {};
    uint8_t password_hash[32];
    uint8_t user_num_length = 0;
    struct locals {
        uint8_t in_buf[256] = {};
        RandomGen myrand;
    } locals; // in c local var order is undefined
              // ensure that the service is hackable by placing myrand next to in_buf

    uint8_t encrypt_buf[16];

    uint32_t user_pos = 0;
    uint8_t password_offset = 0;

    char login_hashhex[65];

    int fd_curr_user = -1;
    int fd_all_users_append = -1;
    int fd_all_users_read = -1;

    uint8_t is_logged = 0;
    uint8_t is_challenged = 0;
    int written;

    uint32_t plain_challenge[4] = {};
    uint8_t encrypted_challenge[16];

    while(1) {
        uint8_t pkt_len = read_packet_or_die(client_socket, locals.in_buf);

        uint8_t &pkt_type = locals.in_buf[0];
        switch (pkt_type) {
            case 0:
                // logins list
                user_num_length = locals.in_buf[1];
                if(user_num_length != 4) {
                    send_error_or_die(client_socket);
                    break;
                }

                memcpy((uint8_t*)&user_pos, &locals.in_buf[2], user_num_length);
                user_pos = __bswap_32(user_pos);

                if (fd_all_users_read == -1) {
                    fd_all_users_read = open("users", O_CREAT|O_RDONLY, 0600);

                    if (fd_all_users_read == -1) {
                        send_error_or_die(client_socket);
                        break;
                    }
                }

                if (!send_user_with_num(client_socket, user_pos, fd_all_users_read)) {
                    send_error_or_die(client_socket);
                }

                break;

            case 1:
                // register
                is_logged = 0;
                login_length = locals.in_buf[1];
                memcpy(login, &locals.in_buf[2], login_length);

                password_length = locals.in_buf[1+login_length+1];
                memcpy(password, &locals.in_buf[1+login_length+1+1], password_length);

                sha256(login, login_length, login_hash);

                hash_to_hex(login_hash, login_hashhex);

                if (fd_curr_user >= 0) {
                    close(fd_curr_user);
                }
                fd_curr_user = open(login_hashhex, O_CREAT|O_EXCL|O_WRONLY, 0600);

                if (fd_all_users_append >= 0) {
                    close(fd_all_users_append);
                }
                fd_all_users_append = open("users", O_CREAT|O_WRONLY|O_APPEND, 0600);

                if (fd_curr_user == -1 || fd_all_users_append == -1) {
                    send_error_or_die(client_socket);
                    break;
                }

                if (init_user(fd_curr_user, fd_all_users_append, login,
                              login_length, password, password_length) == 0) {
                    send_error_or_die(client_socket);
                    break;
                }

                out_buf[0] = 0x0; // 0x0 means OK
                write_packet_or_die(client_socket, out_buf, 1);
                break;


            case 2:
                // start_login_handshake <USERNAME>
                is_logged = 0;
                login_length = locals.in_buf[1];
                memcpy(login, &locals.in_buf[2], login_length);

                sha256(login, login_length, login_hash);
                hash_to_hex(login_hash, login_hashhex);

                if (fd_curr_user >= 0) {
                    close(fd_curr_user);
                }
                fd_curr_user = open(login_hashhex, O_RDWR);

                if (fd_curr_user == -1) {
                    send_error_or_die(client_socket);
                    break;
                }

                memset(password, 0, 256);

                if (get_pass_by_offset(fd_curr_user, 0,
                                   password_name, &password_name_length,
                                   password, &password_length) == 0) {

                    send_error_or_die(client_socket);
                    break;
                }

                if ((login_length != password_name_length) ||
                    (memcmp(login, password_name, password_name_length) != 0)) {
                    send_error_or_die(client_socket);
                    break;
                }

                plain_challenge[0] = locals.myrand.get_random();
                for (int i = 1; i < 4; i += 1) {
                    plain_challenge[i] = 0;
                }

                //
                encrypt(password, (uint8_t*)plain_challenge, encrypted_challenge);

                out_buf[0] = 0x3; // 0x3 means CHALLENGE
                out_buf[1] = 16; // aes block len
                memcpy(&out_buf[2], encrypted_challenge, 16);
                write_packet_or_die(client_socket, out_buf, 1+1+16);
                is_challenged = 1;
                break;
            case 4:
                is_logged = 0;
                if (!is_challenged) {
                    send_error_or_die(client_socket);
                    break;
                }

                if (locals.in_buf[1] != 4) {
                    send_error_or_die(client_socket);
                    break;
                }

                if (memcmp(&locals.in_buf[2], (uint8_t*)plain_challenge, 4) != 0) {
                    send_error_or_die(client_socket);
                    break;
                }
                is_challenged = 0;
                is_logged = 1;

                out_buf[0] = 0x0; // 0x0 means OK
                write_packet_or_die(client_socket, out_buf, 1);
                break;

            case 5:
                // PUT_LOGIN_PASS <OFFSET> <PASS_NAME> <PASS>
                if (!is_logged) {
                    send_error_or_die(client_socket);
                    break;
                }

                if (locals.in_buf[1] != 1) {
                    send_error_or_die(client_socket);
                    break;
                }
                password_offset = locals.in_buf[2];

                if (get_pass_by_offset(fd_curr_user, password_offset,
                                       password_name, &password_name_length,
                                       password, &password_length) == 0) {
                    send_error_or_die(client_socket);
                    break;
                }

                if (password_name_length > 0) {
                    send_error_or_die(client_socket);
                    break;
                }

                password_name_length = locals.in_buf[3];
                memcpy(password_name, &locals.in_buf[4], password_name_length);

                password_length = locals.in_buf[4+password_name_length];
                memcpy(password, &locals.in_buf[4+password_name_length+1], password_length);

                if (set_pass_by_offset(fd_curr_user, password_offset,
                                       password_name, password_name_length,
                                       password, password_length) == 0) {
                    send_error_or_die(client_socket);
                    break;
                }

                out_buf[0] = 0x0; // 0x0 means OK
                write_packet_or_die(client_socket, out_buf, 1);
                break;

            case 6:
                // GET_PASS_NAME <OFFSET> -> PASS_NAME
                if (!is_logged) {
                    send_error_or_die(client_socket);
                    break;
                }

                if (locals.in_buf[1] != 1) {
                    send_error_or_die(client_socket);
                    break;
                }
                password_offset = locals.in_buf[2];

                if (!get_pass_by_offset(fd_curr_user, password_offset,
                                        password_name, &password_name_length,
                                        password, &password_length)) {
                    send_error_or_die(client_socket);
                    break;
                }

                out_buf[0] = 0x7;
                out_buf[1] = password_name_length;
                memcpy(&out_buf[2], password_name, password_name_length);

                write_packet_or_die(client_socket, out_buf, 1+1+password_name_length);
                break;
            case 8:
                // GET_PASS <OFFSET> -> PASS
                if (!is_logged) {
                    send_error_or_die(client_socket);
                    break;
                }

                if (locals.in_buf[1] != 1) {
                    send_error_or_die(client_socket);
                    break;
                }
                password_offset = locals.in_buf[2];

                if (!get_pass_by_offset(fd_curr_user, password_offset,
                                        password_name, &password_name_length,
                                        password, &password_length)) {
                    send_error_or_die(client_socket);
                    break;
                }

                out_buf[0] = 0x9;
                out_buf[1] = password_length;
                memcpy(&out_buf[2], password, password_length);

                write_packet_or_die(client_socket, out_buf, 1+1+password_length);
                break;

            default:
                send_error_or_die(client_socket);
                break;
        }
    }
}


void sigchld_handler(int signo) {
    while (1) {
        int wstatus;
        pid_t pid = waitpid(-1, &wstatus, WNOHANG);
        if (pid == 0 || pid == -1) {
            break;
        }
    }
}

int main(int argc, char ** argv) {
    if (chdir("data") == -1) {
        cerr<<"Err chdir\n";
        exit(1);
    }

    struct sigaction sa;
    sa.sa_handler = sigchld_handler;
    sa.sa_flags = SA_RESTART;
    sigfillset(&sa.sa_mask);
    sigaction(SIGCHLD, &sa, NULL);

    int serv_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (serv_socket == -1) {
        cerr<<"Err socket\n";
        exit(1);
    }

    int one = 1;
    if (setsockopt(serv_socket, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one)) == -1) {
        cerr<<"Err setsockopt\n";
        exit(1);
    }

    struct sockaddr_in my_addr = {};
    my_addr.sin_family = AF_INET;
    my_addr.sin_port = __bswap_16(3255);

    if (bind(serv_socket, (struct sockaddr *) &my_addr, sizeof(my_addr)) == -1) {
        cerr<<"Err bind\n";
        exit(1);
    }

    const int LISTEN_BACKLOG = 256;
    if (listen(serv_socket, LISTEN_BACKLOG) == -1) {
        cerr<<"Err listen\n";
        exit(1);
    }

    struct sockaddr_in peer_addr = {};
    socklen_t peer_addr_size = sizeof(peer_addr);

    while(1) {
        int client_socket = accept(serv_socket, (struct sockaddr*) &peer_addr, &peer_addr_size);

        if (client_socket == -1) {
            continue;
        }

        int fork_result = fork();

        if (fork_result == -1) {
            cerr<<"Err fork\n";
            sleep(1);
            continue;
        }

        if (fork_result == 0) {
            // child
            alarm(10);
            close(serv_socket);
            handle_client(client_socket);
            exit(0);
        } else {
            // parent
            close(client_socket);
        }
    }

    return 0;
}