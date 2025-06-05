// OPC UA Client with Config.json Support
using System;
using System.IO;
using System.Threading.Tasks;
using Opc.Ua;
using Opc.Ua.Client;
using Opc.Ua.Configuration;
using System.Security.Cryptography.X509Certificates;
using System.Text.Json;

// Configuration model
public class OpcUaConfig
{
    public string EndpointUrl { get; set; } = "opc.tcp://192.168.1.100:4840";
    public string Username { get; set; } = "admin";
    public string Password { get; set; } = "password123";
    public bool UseAnonymous { get; set; } = false;
}

class Program
{
    static async Task Main(string[] args)
    {
        // Specify the full path to your config.json file
        var configPath = @"C:\Repository\ControlSystems\Control Systems\C#\AWS Cloud Gateway\config\configOPC.json";
        
        // Load configuration from JSON file
        var config = LoadConfiguration(configPath);
        
        // Create certificate directories with your specific path structure
        var projectRoot = @"C:\Repository\ControlSystems\Control Systems\C#\AWS Cloud Gateway";
        var ownCerts = Path.Combine(projectRoot, "certificates", "own", "certs");
        var ownPrivateKeys = Path.Combine(projectRoot, "certificates", "own", "private");
        var trustedCerts = Path.Combine(projectRoot, "certificates", "trusted", "certs");
        var rejectedCerts = Path.Combine(projectRoot, "certificates", "rejected", "certs");
        
        // Create all necessary directories
        Directory.CreateDirectory(ownCerts);
        Directory.CreateDirectory(ownPrivateKeys);
        Directory.CreateDirectory(trustedCerts);
        Directory.CreateDirectory(rejectedCerts);

        var appConfig = new ApplicationConfiguration()
        {
            ApplicationName = "AWS OPC UA Client (ROG-G16)",
            ApplicationType = ApplicationType.Client,
            ApplicationUri = "urn:AWS-OPC-UA-Client-ROG-G16",
            SecurityConfiguration = new SecurityConfiguration
            {
                ApplicationCertificate = new CertificateIdentifier()
                {
                    StoreType = "Directory",
                    StorePath = ownCerts,
                    SubjectName = "CN=AWS OPC UA Client (ROG-G16), O=YourOrganization, C=US"
                },
                TrustedPeerCertificates = new CertificateTrustList()
                {
                    StoreType = "Directory",
                    StorePath = trustedCerts
                },
                RejectedCertificateStore = new CertificateTrustList()
                {
                    StoreType = "Directory",
                    StorePath = rejectedCerts
                },
                AutoAcceptUntrustedCertificates = true
            },
            TransportQuotas = new TransportQuotas { OperationTimeout = 15000 },
            ClientConfiguration = new ClientConfiguration { DefaultSessionTimeout = 60000 }
        };

        try
        {
            // Validate configuration
            await appConfig.Validate(ApplicationType.Client).ConfigureAwait(false);
            
            // Check if certificate exists, create if it doesn't
            var certificateIdentifier = appConfig.SecurityConfiguration.ApplicationCertificate;
            
            // Try to find existing certificate
            var certificate = await certificateIdentifier.Find(true).ConfigureAwait(false);
            
            if (certificate == null)
            {
                Console.WriteLine("Certificate not found. Creating new certificate...");
                
                // Create a new certificate
                certificate = CertificateFactory.CreateCertificate(
                    certificateIdentifier.StoreType,
                    certificateIdentifier.StorePath,
                    null, // password
                    appConfig.ApplicationUri,
                    appConfig.ApplicationName,
                    certificateIdentifier.SubjectName,
                    null, // domain names
                    2048, // key size
                    DateTime.UtcNow.AddDays(-1), // start time
                    60, // lifetime in months
                    256 // hash size
                );
                
                Console.WriteLine("Certificate created successfully.");
            }
            else
            {
                Console.WriteLine("Using existing certificate.");
            }
            
            // Now try to load the private key
            certificate = await appConfig.SecurityConfiguration.ApplicationCertificate.LoadPrivateKey(null).ConfigureAwait(false);
            
            if (certificate == null)
            {
                throw new ServiceResultException("Failed to load application certificate with private key.");
            }
            
            Console.WriteLine("Configuration validated and certificate loaded successfully.");

            // Use endpoint URL from config
            Console.WriteLine($"Discovering endpoints for: {config.EndpointUrl}");
            
            var endpoint = CoreClientUtils.SelectEndpoint(config.EndpointUrl, true, 15000);
            
            if (endpoint == null)
            {
                throw new Exception("No suitable endpoint found.");
            }
            
            Console.WriteLine($"Selected endpoint: {endpoint.EndpointUrl}");
            Console.WriteLine($"Security Mode: {endpoint.SecurityMode}");
            Console.WriteLine($"Security Policy: {endpoint.SecurityPolicyUri}");
            
            // Create user identity from config
            UserIdentity userIdentity;
            if (config.UseAnonymous)
            {
                Console.WriteLine("Using anonymous authentication");
                userIdentity = new UserIdentity();
            }
            else
            {
                Console.WriteLine($"Using username authentication for user: {config.Username}");
                userIdentity = new UserIdentity(config.Username, config.Password);
            }
            
            Console.WriteLine("Creating session...");
            
            var session = await Session.Create(appConfig, new ConfiguredEndpoint(null, endpoint),
                false, "AWS OPC UA Client Session", 60000, userIdentity, null).ConfigureAwait(false);
            
            Console.WriteLine("Connected and authenticated successfully!");
            
            // Browse the server's address space
            Console.WriteLine("\nBrowsing server nodes...");
            var browser = new Browser(session);
            var references = browser.Browse(ObjectIds.ObjectsFolder);
            
            foreach (var reference in references)
            {
                Console.WriteLine($"Node: {reference.DisplayName} (NodeId: {reference.NodeId})");
                Console.WriteLine($"  Class: {reference.NodeClass}");
                Console.WriteLine($"  Type: {reference.TypeDefinition}");
                
                if (reference.NodeClass == NodeClass.Variable)
                {
                    try
                    {
                        // Convert ExpandedNodeId to NodeId
                        var nodeId = ExpandedNodeId.ToNodeId(reference.NodeId, session.NamespaceUris);
                        var value = session.ReadValue(nodeId);
                        Console.WriteLine($"  Value: {value.Value} (Type: {value.Value?.GetType().Name})");
                        Console.WriteLine($"  Status: {value.StatusCode}");
                        Console.WriteLine($"  Timestamp: {value.ServerTimestamp}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"  Error reading value: {ex.Message}");
                    }
                }
                Console.WriteLine();
            }
            
            // Clean up
            session.Close();
            Console.WriteLine("Session closed successfully.");
        }
        catch (ServiceResultException ex)
        {
            Console.WriteLine($"OPC UA Service Error: {ex.Message}");
            Console.WriteLine($"Status Code: {ex.StatusCode}");
            Console.WriteLine($"Error Type: {ex.GetType().Name}");
            if (ex.InnerException != null)
            {
                Console.WriteLine($"Inner Exception: {ex.InnerException.Message}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"General Error: {ex.Message}");
            Console.WriteLine($"Error Type: {ex.GetType().Name}");
            if (ex.InnerException != null)
            {
                Console.WriteLine($"Inner Exception: {ex.InnerException.Message}");
            }
        }
        
        Console.WriteLine("\nPress any key to exit...");
        Console.ReadKey();
    }
    
    static OpcUaConfig LoadConfiguration(string configPath)
    {
        try
        {
            if (File.Exists(configPath))
            {
                Console.WriteLine($"Loading configuration from: {configPath}");
                var json = File.ReadAllText(configPath);
                var config = JsonSerializer.Deserialize<OpcUaConfig>(json, new JsonSerializerOptions 
                { 
                    PropertyNameCaseInsensitive = true 
                });
                return config ?? new OpcUaConfig();
            }
            else
            {
                Console.WriteLine($"Config file not found at: {configPath}");
                Console.WriteLine("Creating default config.json file...");
                
                // Create default configuration file
                var defaultConfig = new OpcUaConfig();
                var json = JsonSerializer.Serialize(defaultConfig, new JsonSerializerOptions 
                { 
                    WriteIndented = true 
                });
                File.WriteAllText(configPath, json);
                
                Console.WriteLine($"Default config.json created at: {configPath}");
                Console.WriteLine("Please edit the config.json file with your settings and run again.");
                
                return defaultConfig;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error loading configuration: {ex.Message}");
            Console.WriteLine("Using default configuration values.");
            return new OpcUaConfig();
        }
    }
}