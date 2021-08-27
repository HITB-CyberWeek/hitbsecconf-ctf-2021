# The Passman Service

The service is a password manager. It has two parts: a server part which stores the passwords and a client part, which provides the GUI to the user.

The authentication service uses a challenge-response protocol. It encrypts some 32-bit random number, padded with zeroes to block size, with AES128 using the user password as an encryption key. The client decrypts the message and sends the resulting 32-bit random number back.

There is a custom binary protocol between the server and the client.

## The Protocol

The service listens on 3255/TCP port.

Every message is prepended with 1 byte, its length, followed by 1-256 bytes of data.

The first byte of data is a message type. After the message type, the arguments are stored in the same format: the 1-byte argument length and the data. The number of arguments depends on the message type. The answers have the same format.

The message types and their arguments are:

* **type 0**: *user_name(n)*, returns the name of n-th recently registered user, the answer has type 1 and contains the name, if there was an error type 255 is returned
* **type 1**: *register(login, password)*, registers a user. The answer has type 0 on success and type 255 on failure
* **type 2**: *start_login(login)*, start the login proccess. The answer has type 3 and contains the challenge encrypted with the user password
* **type 4**: *continue_login(challenge_response)*, answer the challenge and log in. The answer has type 0, if sucessful or type 255 on failure
* **type 5**: *put_password(offset, password_description, password)*, stores the password. An offset is a number from 0 to 7. Passwords are never overwritten. The answer has type 0 if successful or type 255 on failure
* **type 6**: *get_password_description(offset)*, gets the password description by offset. The zeroth offset always contains the current user login. The answer has type 7 or 255, if error
* **type 8**: *get_password(offset)*, gets the password by offset. The zeroth offset always contains the current user password. The answer has type 8 or 255

### Example of Data Exchange

Here is an example of the register message:

```
   <0xc>       <0x1>       <0x3>      bay       <0x5>         qwerty
 msg_length   msg_type   login_len   login   password_len    password
```

## The Vulnerability

The server uses custom random number generator. It has a state of 32 bytes, which is initialized from /dev/urandom for every user connection.

Here is a full code for the random generation class:

```
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
```

So to generate the next random number, the new state is the *SHA256(old_state)* is calculated and the first 4 bytes of the state are returned.

So if the state was leaked, it is possible to predict new random numbers and authenticate without knowing of password.

In the memory, the state sits right next to the recieve buffer, so some way to get it has to be found.

To exploit the service the packet of this structure has to be sent:

```
   0xff       0x5        0x1        0x1             0xfa                  <0xfa bytes>           0x21
msg_length  msg_type  offset_len   offset   password_description_len   password_description   password_len
```

In the process of handling the data, the 0x21 bytes beyond the buffer will be set as teh password and can be get by the *get_password* call. So the state can be restored and the next challenge answers can be predicted.

The full sploit can be found at [/sploits/passman/sploit.py](../../sploits/passman/sploit.py).


**The fix.** To fix the vuln the additional length check should be added. Also, the random numbers generation method can be modified.

## Random Facts

- The client has a hidden functionality: if one tries to login with **"showlogs"** user, the new window will be opened with the detailed log what is happening will appear
- Also in the Linux version of the client the cipher algorithm is explicitly mentioned
