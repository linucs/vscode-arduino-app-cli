from _typeshed import Incomplete

DEFAULT_CERTS_DIR: str
DEFAULT_CERTS_PARAMS: Incomplete

class TLSCertificateManager:
    """Certificate manager for TLS certificates.

    This class handles certificate generation and retrieval on a Brick basis. By default, all bricks
    share certificates from the default directory (/app/certs).
    Components can use their own certificates by providing a different certs_dir path.
    """
    @classmethod
    def get_or_create_certificates(cls, certs_dir: str = ..., country_name: str = ..., state_or_province_name: str = ..., locality_name: str = ..., organization_name: str = ..., common_name: str = ..., validity_days: int = ...) -> tuple[str, str]:
        '''Get or create TLS certificates at the specified path.

        By default, uses shared certificates in /app/certs. If a different certs_dir is provided,
        uses certificates specific to that directory (useful for brick-specific certificates).

        Concurrent access is managed to prevent race conditions when multiple bricks attempt to
        access certificates simultaneously.

        Args:
            certs_dir (str, optional): Directory for certificates. Defaults to /app/certs (shared
                by all bricks). Provide a different path for brick-specific certificates.
            country_name (str, optional): Country name for the certificate. Defaults to "IT".
            state_or_province_name (str, optional): State or province name for the certificate.
                Defaults to "Piedmont".
            locality_name (str, optional): Locality name for the certificate. Defaults to "Turin".
            organization_name (str, optional): Organization name for the certificate. Defaults to "Arduino".
            common_name (str, optional): Common name for the certificate. Defaults to "0.0.0.0".
            validity_days (int, optional): Certificate validity period in days. Defaults to 365.

        Returns:
            tuple[str, str]: Paths to (certificate_file, private_key_file)

        Raises:
            RuntimeError: If certificate generation fails.
        '''
    @classmethod
    def certificates_exist(cls, certs_dir: str = ...) -> bool:
        """Check if TLS certificates exist in the given directory.

        Args:
            certs_dir (str, optional): Directory for certificates.
                Defaults to /app/certs.

        Returns:
            bool: True if both certificate and key files exist, False otherwise.
        """
    @classmethod
    def get_certificates_paths(cls, certs_dir: str = ...) -> tuple[str, str]:
        """Get the paths to the TLS certificate and private key files.

        Args:
            certs_dir (str, optional): Directory for certificates. Defaults to /app/certs.
        Returns:
            tuple[str, str]: Paths to certificate_file and private_key_file
        """
    @classmethod
    def get_certificate_path(cls, certs_dir: str = ...) -> str:
        """Get the path to the TLS certificate file.

        Args:
            certs_dir (str, optional): Directory for certificates. Defaults to /app/certs.

        Returns:
            str: Path to the certificate file.
        """
    @classmethod
    def get_private_key_path(cls, certs_dir: str = ...) -> str:
        """Get the path to the TLS private key file.

        Args:
            certs_dir (str, optional): Directory for certificates. Defaults to /app/certs.

        Returns:
            str: Path to the private key file.
        """
