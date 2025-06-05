using System.Linq;
using System.Collections.Generic;// OPC UA Client with Config.json Support
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
            
            // Browse the server's address space and PLC tags
            Console.WriteLine("\nBrowsing server nodes and PLC tags...");
            var browser = new Browser(session);
            
            // First, collect all variable nodes
            var allVariables = new List<(ReferenceDescription reference, int depth)>();
            CollectVariablesRecursively(browser, ObjectIds.ObjectsFolder, 0, 3, allVariables);
            
            Console.WriteLine($"\nFound {allVariables.Count} variables. Reading values in batches...");
            
            // Read all variables in batches for better performance
            ReadVariablesInBatches(session, allVariables, 50); // Read 50 at a time
            
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
    
    static void CollectVariablesRecursively(Browser browser, NodeId nodeId, int depth, int maxDepth, List<(ReferenceDescription reference, int depth)> variables)
    {
        if (depth > maxDepth) return;
        
        try
        {
            var references = browser.Browse(nodeId);
            
            foreach (var reference in references)
            {
                // Skip type definitions
                if (reference.NodeClass == NodeClass.ObjectType || reference.NodeClass == NodeClass.VariableType)
                {
                    continue;
                }
                
                if (reference.NodeClass == NodeClass.Variable)
                {
                    variables.Add((reference, depth));
                }
                
                // Recursively browse child nodes for Objects only
                if (reference.NodeClass == NodeClass.Object)
                {
                    var childNodeId = ExpandedNodeId.ToNodeId(reference.NodeId, browser.Session.NamespaceUris);
                    CollectVariablesRecursively(browser, childNodeId, depth + 1, maxDepth, variables);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error browsing node {nodeId}: {ex.Message}");
        }
    }
    
    static void ReadVariablesInBatches(Session session, List<(ReferenceDescription reference, int depth)> variables, int batchSize)
    {
        var stopwatch = System.Diagnostics.Stopwatch.StartNew();
        
        for (int i = 0; i < variables.Count; i += batchSize)
        {
            var batch = variables.Skip(i).Take(batchSize).ToList();
            var readValueIds = new ReadValueIdCollection();
            
            // Prepare batch read request
            foreach (var (reference, depth) in batch)
            {
                try
                {
                    var nodeId = ExpandedNodeId.ToNodeId(reference.NodeId, session.NamespaceUris);
                    readValueIds.Add(new ReadValueId
                    {
                        NodeId = nodeId,
                        AttributeId = Attributes.Value
                    });
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error preparing read for {reference.DisplayName}: {ex.Message}");
                }
            }
            
            if (readValueIds.Count == 0) continue;
            
            try
            {
                // Batch read - much faster!
                DataValueCollection results;
                DiagnosticInfoCollection diagnosticInfos;
                session.Read(null, 0, TimestampsToReturn.Server, readValueIds, out results, out diagnosticInfos);
                
                // Display results
                for (int j = 0; j < batch.Count && j < results.Count; j++)
                {
                    var (reference, depth) = batch[j];
                    var result = results[j];
                    var indent = new string(' ', depth * 2);
                    
                    Console.WriteLine($"{indent}Tag: {reference.DisplayName}");
                    Console.WriteLine($"{indent}  NodeId: {reference.NodeId}");
                    
                    // Standardized status format
                    string statusText;
                    object displayValue;
                    string dataType = "Unknown";
                    DateTime displayTimestamp = DateTime.MinValue;
                    
                    if (StatusCode.IsGood(result.StatusCode))
                    {
                        statusText = "Good";
                        displayValue = result.Value;
                        displayTimestamp = result.ServerTimestamp;
                        dataType = result.Value?.GetType().Name ?? "Unknown";
                    }
                    else if (StatusCode.IsUncertain(result.StatusCode))
                    {
                        statusText = $"Uncertain - {result.StatusCode}";
                        displayValue = result.Value ?? GetDefaultValue(result.Value);
                        displayTimestamp = result.ServerTimestamp != DateTime.MinValue ? result.ServerTimestamp : DateTime.Now;
                        dataType = result.Value?.GetType().Name ?? "Unknown";
                    }
                    else // Bad status
                    {
                        statusText = $"Bad - {result.StatusCode}";
                        displayValue = GetDefaultValue(result.Value);
                        displayTimestamp = DateTime.Now; // Hold current timestamp for bad values
                        
                        // Try to determine data type from the node if possible
                        try
                        {
                            var nodeId = ExpandedNodeId.ToNodeId(reference.NodeId, session.NamespaceUris);
                            var dataTypeIds = new ReadValueIdCollection
                            {
                                new ReadValueId { NodeId = nodeId, AttributeId = Attributes.DataType }
                            };
                            DataValueCollection dataTypeResults;
                            DiagnosticInfoCollection diagnostics;
                            session.Read(null, 0, TimestampsToReturn.Neither, dataTypeIds, out dataTypeResults, out diagnostics);
                            
                            if (dataTypeResults?.Count > 0 && dataTypeResults[0].Value != null)
                            {
                                var dataTypeNodeId = (NodeId)dataTypeResults[0].Value;
                                dataType = GetDataTypeName(dataTypeNodeId);
                            }
                        }
                        catch
                        {
                            dataType = "Unknown";
                        }
                    }
                    
                    Console.WriteLine($"{indent}  Status: {statusText}");
                    Console.WriteLine($"{indent}  Value: {displayValue}");
                    Console.WriteLine($"{indent}  DataType: {dataType}");
                    Console.WriteLine($"{indent}  Timestamp: {displayTimestamp}");
                    Console.WriteLine();
                }
                
                Console.WriteLine($"Batch {(i / batchSize) + 1}: Read {results.Count} tags in {stopwatch.ElapsedMilliseconds}ms");
                stopwatch.Restart();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error reading batch: {ex.Message}");
            }
        }
    }
    
    static object GetDefaultValue(object originalValue)
    {
        // If we have the original value type info, use appropriate defaults
        if (originalValue != null)
        {
            var type = originalValue.GetType();
            if (type == typeof(bool)) return false;
            if (type == typeof(int) || type == typeof(short) || type == typeof(long)) return 0;
            if (type == typeof(float) || type == typeof(double) || type == typeof(decimal)) return 0.0;
            if (type == typeof(string)) return "";
        }
        
        // Default fallback - assume numeric
        return 0.0;
    }
    
    static string GetDataTypeName(NodeId dataTypeNodeId)
    {
        // Common OPC UA data type mappings
        var wellKnownTypes = new Dictionary<uint, string>
        {
            { 1, "Boolean" },
            { 2, "SByte" },
            { 3, "Byte" },
            { 4, "Int16" },
            { 5, "UInt16" },
            { 6, "Int32" },
            { 7, "UInt32" },
            { 8, "Int64" },
            { 9, "UInt64" },
            { 10, "Float" },
            { 11, "Double" },
            { 12, "String" },
            { 13, "DateTime" }
        };
        
        if (dataTypeNodeId.NamespaceIndex == 0 && wellKnownTypes.ContainsKey(dataTypeNodeId.Identifier as uint? ?? 0))
        {
            return wellKnownTypes[dataTypeNodeId.Identifier as uint? ?? 0];
        }
        
        return "Unknown";
    }
    
    // Keep the old method for reference (not used anymore)
    static void BrowseNodeRecursively(Session session, Browser browser, NodeId nodeId, int depth, int maxDepth)
    {
        if (depth > maxDepth) return;
        
        var indent = new string(' ', depth * 2);
        
        try
        {
            var references = browser.Browse(nodeId);
            
            foreach (var reference in references)
            {
                // Skip type definitions - we only want actual instances
                if (reference.NodeClass == NodeClass.ObjectType || reference.NodeClass == NodeClass.VariableType)
                {
                    continue;
                }
                
                Console.WriteLine($"{indent}Node: {reference.DisplayName} (NodeId: {reference.NodeId})");
                Console.WriteLine($"{indent}  Class: {reference.NodeClass}");
                Console.WriteLine($"{indent}  Type: {reference.TypeDefinition}");
                
                if (reference.NodeClass == NodeClass.Variable)
                {
                    try
                    {
                        // Convert ExpandedNodeId to NodeId
                        var varNodeId = ExpandedNodeId.ToNodeId(reference.NodeId, session.NamespaceUris);
                        var value = session.ReadValue(varNodeId);
                        
                        if (StatusCode.IsGood(value.StatusCode))
                        {
                            Console.WriteLine($"{indent}  Value: {value.Value} (Type: {value.Value?.GetType().Name})");
                            Console.WriteLine($"{indent}  Status: {value.StatusCode}");
                            Console.WriteLine($"{indent}  Timestamp: {value.ServerTimestamp}");
                        }
                        else
                        {
                            Console.WriteLine($"{indent}  Status: {value.StatusCode} (No current value)");
                        }
                        
                        // Try to read additional attributes for PLC tags
                        try
                        {
                            var readValueIds = new ReadValueIdCollection
                            {
                                new ReadValueId
                                {
                                    NodeId = varNodeId,
                                    AttributeId = Attributes.Description
                                }
                            };
                            
                            DataValueCollection results;
                            DiagnosticInfoCollection diagnosticInfos;
                            session.Read(null, 0, TimestampsToReturn.Neither, readValueIds, out results, out diagnosticInfos);
                            
                            if (results != null && results.Count > 0 && results[0].Value != null)
                            {
                                Console.WriteLine($"{indent}  Description: {results[0].Value}");
                            }
                        }
                        catch { /* Description not available */ }
                        
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"{indent}  Error reading value: {ex.Message}");
                    }
                }
                
                // Recursively browse child nodes (especially for PLC objects)
                if (reference.NodeClass == NodeClass.Object)
                {
                    var childNodeId = ExpandedNodeId.ToNodeId(reference.NodeId, session.NamespaceUris);
                    BrowseNodeRecursively(session, browser, childNodeId, depth + 1, maxDepth);
                }
                
                Console.WriteLine();
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"{indent}Error browsing node {nodeId}: {ex.Message}");
        }
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