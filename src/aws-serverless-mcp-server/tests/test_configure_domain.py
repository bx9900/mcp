# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.
"""Tests for the configure_domain module."""

import pytest
from unittest.mock import patch, MagicMock
from awslabs.aws_serverless_mcp_server.models import ConfigureDomainRequest
from awslabs.aws_serverless_mcp_server.tools.webapps.configure_domain import configure_domain


class TestConfigureDomain:
    """Tests for the configure_domain function."""

    @pytest.mark.asyncio
    async def test_configure_domain_with_route53(self):
        """Test configuring a domain with Route53 record creation."""
        # Create a mock request
        request = ConfigureDomainRequest(
            project_name="test-project",
            domain_name="test.example.com",
            certificate_arn="arn:aws:acm:us-east-1:123456789012:certificate/abcdef12-3456-7890-abcd-ef1234567890",
            hosted_zone_id="Z1234567890ABCDEFGHIJ",
            create_route53_record=True
        )

        # Mock boto3 session and clients
        mock_session = MagicMock()
        mock_cloudfront_client = MagicMock()
        mock_route53_client = MagicMock()
        
        mock_session.client.side_effect = lambda service: {
            'cloudfront': mock_cloudfront_client,
            'route53': mock_route53_client
        }[service]
        
        # Mock CloudFront get_distribution_config response
        mock_cloudfront_client.get_distribution_config.return_value = {
            'ETag': 'ETAGVALUE',
            'DistributionConfig': {
                'CallerReference': 'test-reference',
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': 'S3Origin',
                            'DomainName': 'test-bucket.s3.amazonaws.com',
                            'S3OriginConfig': {
                                'OriginAccessIdentity': ''
                            }
                        }
                    ]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': 'S3Origin',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'AllowedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD']
                    }
                },
                'Comment': 'Test distribution',
                'Enabled': True
            }
        }
        
        # Mock CloudFront update_distribution response
        mock_cloudfront_client.update_distribution.return_value = {
            'Distribution': {
                'Id': 'ABCDEF12345',
                'ARN': 'arn:aws:cloudfront::123456789012:distribution/ABCDEF12345',
                'Status': 'InProgress',
                'LastModifiedTime': '2023-05-21T12:00:00Z',
                'DomainName': 'd1234abcdef.cloudfront.net',
                'DistributionConfig': {
                    'CallerReference': 'test-reference',
                    'Aliases': {
                        'Quantity': 1,
                        'Items': ['test.example.com']
                    },
                    'ViewerCertificate': {
                        'ACMCertificateArn': 'arn:aws:acm:us-east-1:123456789012:certificate/abcdef12-3456-7890-abcd-ef1234567890',
                        'SSLSupportMethod': 'sni-only',
                        'MinimumProtocolVersion': 'TLSv1.2_2021'
                    }
                }
            }
        }
        
        # Mock Route53 change_resource_record_sets response
        mock_route53_client.change_resource_record_sets.return_value = {
            'ChangeInfo': {
                'Id': '/change/C1234567890ABCDEFGHIJ',
                'Status': 'PENDING',
                'SubmittedAt': '2023-05-21T12:00:00Z'
            }
        }

        with patch('boto3.Session', return_value=mock_session):
            # Call the function
            result = await configure_domain(request)

            # Verify the result
            assert result["success"] is True
            assert "Custom domain test.example.com configured successfully" in result["message"]
            assert result["cloudfront_domain"] == "d1234abcdef.cloudfront.net"
            assert result["route53_record_created"] is True
            assert result["route53_change_id"] == "/change/C1234567890ABCDEFGHIJ"

            # Verify CloudFront client was called with the correct parameters
            mock_cloudfront_client.get_distribution_config.assert_called_once_with(Id="test-project-distribution")
            
            mock_cloudfront_client.update_distribution.assert_called_once()
            args, kwargs = mock_cloudfront_client.update_distribution.call_args
            assert kwargs["Id"] == "test-project-distribution"
            assert kwargs["IfMatch"] == "ETAGVALUE"
            assert kwargs["DistributionConfig"]["Aliases"]["Quantity"] == 1
            assert kwargs["DistributionConfig"]["Aliases"]["Items"] == ["test.example.com"]
            assert kwargs["DistributionConfig"]["ViewerCertificate"]["ACMCertificateArn"] == "arn:aws:acm:us-east-1:123456789012:certificate/abcdef12-3456-7890-abcd-ef1234567890"
            
            # Verify Route53 client was called with the correct parameters
            mock_route53_client.change_resource_record_sets.assert_called_once()
            args, kwargs = mock_route53_client.change_resource_record_sets.call_args
            assert kwargs["HostedZoneId"] == "Z1234567890ABCDEFGHIJ"
            assert kwargs["ChangeBatch"]["Changes"][0]["Action"] == "UPSERT"
            assert kwargs["ChangeBatch"]["Changes"][0]["ResourceRecordSet"]["Name"] == "test.example.com"
            assert kwargs["ChangeBatch"]["Changes"][0]["ResourceRecordSet"]["Type"] == "A"
            assert kwargs["ChangeBatch"]["Changes"][0]["ResourceRecordSet"]["AliasTarget"]["DNSName"] == "d1234abcdef.cloudfront.net"

    @pytest.mark.asyncio
    async def test_configure_domain_without_route53(self):
        """Test configuring a domain without Route53 record creation."""
        # Create a mock request
        request = ConfigureDomainRequest(
            project_name="test-project",
            domain_name="test.example.com",
            certificate_arn="arn:aws:acm:us-east-1:123456789012:certificate/abcdef12-3456-7890-abcd-ef1234567890",
            create_route53_record=False
        )

        # Mock boto3 session and clients
        mock_session = MagicMock()
        mock_cloudfront_client = MagicMock()
        mock_route53_client = MagicMock()
        
        mock_session.client.side_effect = lambda service: {
            'cloudfront': mock_cloudfront_client,
            'route53': mock_route53_client
        }[service]
        
        # Mock CloudFront get_distribution_config response
        mock_cloudfront_client.get_distribution_config.return_value = {
            'ETag': 'ETAGVALUE',
            'DistributionConfig': {
                'CallerReference': 'test-reference',
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': 'S3Origin',
                            'DomainName': 'test-bucket.s3.amazonaws.com',
                            'S3OriginConfig': {
                                'OriginAccessIdentity': ''
                            }
                        }
                    ]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': 'S3Origin',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'AllowedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD']
                    }
                },
                'Comment': 'Test distribution',
                'Enabled': True
            }
        }
        
        # Mock CloudFront update_distribution response
        mock_cloudfront_client.update_distribution.return_value = {
            'Distribution': {
                'Id': 'ABCDEF12345',
                'ARN': 'arn:aws:cloudfront::123456789012:distribution/ABCDEF12345',
                'Status': 'InProgress',
                'LastModifiedTime': '2023-05-21T12:00:00Z',
                'DomainName': 'd1234abcdef.cloudfront.net',
                'DistributionConfig': {
                    'CallerReference': 'test-reference',
                    'Aliases': {
                        'Quantity': 1,
                        'Items': ['test.example.com']
                    },
                    'ViewerCertificate': {
                        'ACMCertificateArn': 'arn:aws:acm:us-east-1:123456789012:certificate/abcdef12-3456-7890-abcd-ef1234567890',
                        'SSLSupportMethod': 'sni-only',
                        'MinimumProtocolVersion': 'TLSv1.2_2021'
                    }
                }
            }
        }

        with patch('boto3.Session', return_value=mock_session):
            # Call the function
            result = await configure_domain(request)

            # Verify the result
            assert result["success"] is True
            assert "Custom domain test.example.com configured successfully" in result["message"]
            assert result["cloudfront_domain"] == "d1234abcdef.cloudfront.net"
            assert result["route53_record_created"] is False
            assert "No Route53 record was created" in result["note"]

            # Verify CloudFront client was called with the correct parameters
            mock_cloudfront_client.get_distribution_config.assert_called_once_with(Id="test-project-distribution")
            
            mock_cloudfront_client.update_distribution.assert_called_once()
            args, kwargs = mock_cloudfront_client.update_distribution.call_args
            assert kwargs["Id"] == "test-project-distribution"
            assert kwargs["IfMatch"] == "ETAGVALUE"
            assert kwargs["DistributionConfig"]["Aliases"]["Quantity"] == 1
            assert kwargs["DistributionConfig"]["Aliases"]["Items"] == ["test.example.com"]
            assert kwargs["DistributionConfig"]["ViewerCertificate"]["ACMCertificateArn"] == "arn:aws:acm:us-east-1:123456789012:certificate/abcdef12-3456-7890-abcd-ef1234567890"
            
            # Verify Route53 client was not called
            mock_route53_client.change_resource_record_sets.assert_not_called()

    @pytest.mark.asyncio
    async def test_configure_domain_cloudfront_error(self):
        """Test configuring a domain with CloudFront error."""
        # Create a mock request
        request = ConfigureDomainRequest(
            project_name="test-project",
            domain_name="test.example.com",
            certificate_arn="arn:aws:acm:us-east-1:123456789012:certificate/abcdef12-3456-7890-abcd-ef1234567890"
        )

        # Mock boto3 session and clients
        mock_session = MagicMock()
        mock_cloudfront_client = MagicMock()
        
        mock_session.client.side_effect = lambda service: {
            'cloudfront': mock_cloudfront_client,
            'route53': MagicMock()
        }[service]
        
        # Mock CloudFront get_distribution_config to raise an exception
        error_message = "The specified distribution does not exist"
        mock_cloudfront_client.get_distribution_config.side_effect = Exception(error_message)

        with patch('boto3.Session', return_value=mock_session):
            # Call the function
            result = await configure_domain(request)

            # Verify the result
            assert result["success"] is False
            assert "Failed to configure custom domain" in result["message"]
            assert error_message in result["error"]
