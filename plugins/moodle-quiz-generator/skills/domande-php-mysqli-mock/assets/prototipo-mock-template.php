<?php
/* =====================================================================
 * Mock di mysqli per CodeRunner (PHP)
 * Simula connessione e query senza un vero server MySQL.
 *
 * REQUISITO: l'estensione mysqli NON deve essere caricata nel PHP di Jobe
 * (verifica con: php -m | grep -i mysqli), altrimenti le dichiarazioni
 * qui sotto danno "Cannot redeclare".
 *
 * Nota Twig: in questo codice non usare mai due graffe aperte di seguito,
 * né una graffa seguita da cancelletto o percento.
 * ===================================================================== */

define('MYSQLI_ASSOC', 1);
define('MYSQLI_NUM', 2);
define('MYSQLI_BOTH', 3);
define('MYSQLI_REPORT_OFF', 0);
define('MYSQLI_REPORT_ERROR', 1);
define('MYSQLI_REPORT_STRICT', 2);
define('MYSQLI_REPORT_ALL', 255);

class mysqli_sql_exception extends RuntimeException {}

final class FakeDB
{
    // ---- configurazione (impostata dal codice di test con FakeDB::configure) ----
    public static $hosts = ['localhost', '127.0.0.1'];
    public static $port = null;          // null = accetta qualsiasi porta
    public static $user = 'root';
    public static $password = '';
    public static $database = '';
    public static $queries = [];         // query (o /regex/) => risultato
    public static $exceptions = false;   // true = comportamento predefinito di PHP 8.1+
    public static $unknownQueryError = 'Query non riconosciuta dal correttore';

    // ---- stato interno ----
    public static $log = [];
    public static $connectErrno = 0;
    public static $connectError = null;

    public static function configure(array $config)
    {
        foreach ($config as $key => $value) {
            if (!property_exists(self::class, $key)) {
                throw new InvalidArgumentException("FakeDB: opzione sconosciuta '$key'");
            }
            self::${$key} = $value;
        }
    }

    // Minuscolo, niente backtick, spazi compattati, niente spazi attorno a , = ( ) < >
    public static function normalize($sql)
    {
        $sql = str_replace('`', '', strtolower(trim((string)$sql)));
        $sql = rtrim($sql, "; \t\r\n");
        $sql = preg_replace('/\s+/', ' ', $sql);
        return preg_replace('/\s*([,=()<>])\s*/', '$1', $sql);
    }

    public static function checkConnection($host, $user, $password, $database, $port)
    {
        $host = $host ?? 'localhost';
        $user = (string)$user;
        $password = (string)$password;
        $database = (string)$database;

        if (!in_array($host, self::$hosts, true)) {
            return [2002, "php_network_getaddresses: getaddrinfo for $host failed: Name or service not known"];
        }
        if (self::$port !== null && $port !== null && (int)$port !== (int)self::$port) {
            return [2002, 'Connection refused'];
        }
        if ($user !== self::$user || $password !== self::$password) {
            $usingPassword = $password === '' ? 'NO' : 'YES';
            return [1045, "Access denied for user '$user'@'localhost' (using password: $usingPassword)"];
        }
        if ($database !== '' && $database !== self::$database) {
            return [1049, "Unknown database '$database'"];
        }
        return null;
    }

    public static function lookup($sql)
    {
        $normalized = self::normalize($sql);
        foreach (self::$queries as $pattern => $result) {
            $pattern = (string)$pattern;
            $isRegex = strlen($pattern) > 1 && $pattern[0] === '/';
            $match = $isRegex
                ? preg_match($pattern, $normalized) === 1
                : self::normalize($pattern) === $normalized;
            if ($match) {
                return [true, $result];
            }
        }
        return [false, null];
    }

    // ---- funzioni di supporto per i test ----
    public static function executedQueries()
    {
        $out = [];
        foreach (self::$log as $entry) {
            if ($entry[0] === 'query') {
                $out[] = $entry[1];
            }
        }
        return $out;
    }

    public static function connectionClosed()
    {
        foreach (self::$log as $entry) {
            if ($entry[0] === 'close') {
                return true;
            }
        }
        return false;
    }
}

class mysqli
{
    public $connect_errno = 0;
    public $connect_error = null;
    public $errno = 0;
    public $error = '';
    public $affected_rows = 0;
    public $insert_id = 0;
    private $db = '';
    private $connected = false;
    private $closed = false;

    public function __construct($hostname = null, $username = null, $password = null,
                                $database = '', $port = null, $socket = null)
    {
        FakeDB::$log[] = ['connect', $hostname, $username, $password, $database];
        $error = FakeDB::checkConnection($hostname, $username, $password, $database, $port);
        if ($error !== null) {
            $this->connect_errno = $error[0];
            $this->connect_error = $error[1];
            FakeDB::$connectErrno = $error[0];
            FakeDB::$connectError = $error[1];
            if (FakeDB::$exceptions) {
                throw new mysqli_sql_exception($error[1], $error[0]);
            }
            return;
        }
        FakeDB::$connectErrno = 0;
        FakeDB::$connectError = null;
        $this->connected = true;
        $this->db = (string)$database;
    }

    private function ensureUsable()
    {
        if ($this->closed) {
            throw new Error('mysqli object is already closed');
        }
        if (!$this->connected) {
            throw new Error('mysqli object is not fully initialized');
        }
    }

    private function fail($errno, $message)
    {
        $this->errno = $errno;
        $this->error = $message;
        if (FakeDB::$exceptions) {
            throw new mysqli_sql_exception($message, $errno);
        }
        return false;
    }

    public function query($query)
    {
        $this->ensureUsable();
        FakeDB::$log[] = ['query', $query];
        $this->errno = 0;
        $this->error = '';

        if ($this->db === '') {
            return $this->fail(1046, 'No database selected');
        }
        [$found, $result] = FakeDB::lookup($query);
        if (!$found) {
            return $this->fail(1064, FakeDB::$unknownQueryError);
        }
        if ($result === true) {                       // INSERT/UPDATE/DELETE generica
            $this->affected_rows = 0;
            return true;
        }
        if (is_int($result)) {                        // numero di righe coinvolte
            $this->affected_rows = $result;
            return true;
        }
        if (is_array($result) && isset($result['error'])) {   // errore simulato
            return $this->fail($result['error'][0], $result['error'][1]);
        }
        if (is_array($result) && (isset($result['affected']) || isset($result['insert_id']))) {
            $this->affected_rows = $result['affected'] ?? 0;
            $this->insert_id = $result['insert_id'] ?? 0;
            return true;
        }
        $res = new mysqli_result($result);            // SELECT: lista di righe
        $this->affected_rows = $res->num_rows;
        return $res;
    }

    public function select_db($database)
    {
        $this->ensureUsable();
        if ($database !== FakeDB::$database) {
            return $this->fail(1049, "Unknown database '$database'");
        }
        $this->db = $database;
        return true;
    }

    public function set_charset($charset)
    {
        $this->ensureUsable();
        return true;
    }

    public function real_escape_string($string)
    {
        $this->ensureUsable();
        return addslashes($string);
    }

    public function close()
    {
        $this->ensureUsable();
        $this->closed = true;
        FakeDB::$log[] = ['close'];
        return true;
    }
}

class mysqli_result implements IteratorAggregate
{
    public $num_rows = 0;
    public $field_count = 0;
    private $rows = [];
    private $position = 0;

    public function __construct(array $rows)
    {
        // Come il vero mysqli (query non preparate): tutti i valori arrivano come stringhe
        foreach ($rows as $row) {
            $this->rows[] = array_map(function ($v) {
                return $v === null ? null : (string)$v;
            }, $row);
        }
        $this->num_rows = count($this->rows);
        $this->field_count = $this->num_rows ? count($this->rows[0]) : 0;
    }

    public function fetch_assoc()
    {
        return $this->position < $this->num_rows ? $this->rows[$this->position++] : null;
    }

    public function fetch_row()
    {
        $r = $this->fetch_assoc();
        return $r === null ? null : array_values($r);
    }

    public function fetch_object()
    {
        $r = $this->fetch_assoc();
        return $r === null ? null : (object)$r;
    }

    public function fetch_array($mode = MYSQLI_BOTH)
    {
        $r = $this->fetch_assoc();
        if ($r === null || $mode === MYSQLI_ASSOC) {
            return $r;
        }
        if ($mode === MYSQLI_NUM) {
            return array_values($r);
        }
        $both = [];
        $i = 0;
        foreach ($r as $k => $v) {
            $both[$i++] = $v;
            $both[$k] = $v;
        }
        return $both;
    }

    public function fetch_all($mode = MYSQLI_NUM)
    {
        $all = [];
        while (($r = $this->fetch_array($mode)) !== null) {
            $all[] = $r;
        }
        return $all;
    }

    public function data_seek($offset)
    {
        if ($offset < 0 || $offset >= $this->num_rows) {
            return false;
        }
        $this->position = $offset;
        return true;
    }

    public function free() {}

    public function getIterator(): Iterator
    {
        $rest = array_slice($this->rows, $this->position);
        $this->position = $this->num_rows;
        return new ArrayIterator($rest);
    }
}

// ---- Stile procedurale (i type hint producono gli stessi TypeError del vero mysqli) ----
function mysqli_connect($hostname = null, $username = null, $password = null,
                        $database = '', $port = null, $socket = null)
{
    $conn = new mysqli($hostname, $username, $password, $database, $port, $socket);
    return $conn->connect_errno ? false : $conn;
}
function mysqli_connect_errno() { return FakeDB::$connectErrno; }
function mysqli_connect_error() { return FakeDB::$connectError; }
function mysqli_query(mysqli $mysql, $query) { return $mysql->query($query); }
function mysqli_error(mysqli $mysql) { return $mysql->error; }
function mysqli_errno(mysqli $mysql) { return $mysql->errno; }
function mysqli_select_db(mysqli $mysql, $database) { return $mysql->select_db($database); }
function mysqli_set_charset(mysqli $mysql, $charset) { return $mysql->set_charset($charset); }
function mysqli_real_escape_string(mysqli $mysql, $string) { return $mysql->real_escape_string($string); }
function mysqli_affected_rows(mysqli $mysql) { return $mysql->affected_rows; }
function mysqli_insert_id(mysqli $mysql) { return $mysql->insert_id; }
function mysqli_close(mysqli $mysql) { return $mysql->close(); }
function mysqli_fetch_assoc(mysqli_result $result) { return $result->fetch_assoc(); }
function mysqli_fetch_row(mysqli_result $result) { return $result->fetch_row(); }
function mysqli_fetch_object(mysqli_result $result) { return $result->fetch_object(); }
function mysqli_fetch_array(mysqli_result $result, $mode = MYSQLI_BOTH) { return $result->fetch_array($mode); }
function mysqli_fetch_all(mysqli_result $result, $mode = MYSQLI_NUM) { return $result->fetch_all($mode); }
function mysqli_num_rows(mysqli_result $result) { return $result->num_rows; }
function mysqli_num_fields(mysqli_result $result) { return $result->field_count; }
function mysqli_data_seek(mysqli_result $result, $offset) { return $result->data_seek($offset); }
function mysqli_free_result(mysqli_result $result) { $result->free(); }
function mysqli_report($flags)
{
    FakeDB::$exceptions = (bool)($flags & MYSQLI_REPORT_STRICT);
    return true;
}

/* ======================= fine del mock ======================= */

{{ TEST.testcode }}
?>
{{ STUDENT_ANSWER }}
